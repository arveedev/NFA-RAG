import os
import re
import streamlit as st
from supabase import create_client
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- 1. SETUP & INITIALIZATION ---
load_dotenv()
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY"))
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Custom Bot Avatar (Animated GIF for personality)
BOT_AVATAR = "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExNHJueGZ3bmZ3bmZ3bmZ3bmZ3bmZ3bmZ3bmZ3bmZ3bmZ3bmZ3/3o7TKSjP8M6E6v9m9u/giphy.gif"

# --- 2. THE AI PERSONA (SYSTEM PROMPT) ---
SYSTEM_INSTRUCTION = """You are the Lead Technical Expert for NFA Standard Operating Procedures. 
Your tone is professional, authoritative, and helpful, with a touch of dry, seasoned wit.

CRITICAL EXPERT GUIDELINES:
1. TECHNICAL TRANSLATION: If a user asks a 'layman' question (e.g., 'age of rice'), you must interpret this as technical concepts (e.g., 'Storage Longevity', 'Stock Disposition', or 'FIFO').
2. SOURCE TRUTH: Use ONLY the provided CONTEXT. If the specific answer isn't there, state exactly what you see and suggest related technical terms.
3. CITATION: You MUST provide the SOP NUMBER and the [Source Link] for every claim.
4. MOBILE CLARITY: Ensure links are presented clearly so they are easy to tap on mobile devices."""

# --- 3. UTILITY FUNCTIONS ---
def fix_domino_url(url):
    if not url: return url
    if "nfaweb.nfa.gov.ph" in url and "/webapp/msd/sopweb.nsf/" not in url:
        url = url.replace("https://nfaweb.nfa.gov.ph/", "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/")
        url = re.sub(r'(?<!:)/{2,}', '/', url)
    return url

# --- 4. STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="NFA SOP Expert", page_icon="🤖", layout="centered")

# Mobile-friendly CSS for link visibility
st.markdown("""
    <style>
    .stChatMessage a {
        color: #1f77b4 !important;
        text-decoration: underline !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 NFA SOP Expert AI")
st.caption("Advanced Retrieval-Augmented Expert System (V2.0)")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. THE SEARCH ENGINE (HYBRID + QUERY EXPANSION) ---
def get_expert_context(user_query):
    """Refined search that identifies technical terms before querying the DB."""
    
    # STEP 1: Expert Term Expansion
    # We ask Gemini to give us technical keywords for better DB retrieval
    expansion_prompt = f"The user asked: '{user_query}'. Identify 3 technical NFA keywords or SOP codes related to this. Output only the keywords, comma separated."
    keywords_resp = gemini_client.models.generate_content(model='gemini-2.5-flash', contents=expansion_prompt)
    expanded_terms = [user_query] + keywords_resp.text.strip().split(',')

    db_results = []
    seen_links = set()

    # STEP 2: Hybrid Search (Codes + Vectors)
    for term in expanded_terms:
        # A. Regex for specific codes (TS-SQ04, etc)
        codes = re.findall(r'\b[A-Z]{2,4}-[A-Z0-9]{2,5}\b', term.upper())
        for code in codes:
            kw_res = supabase.table("sops").select("*").ilike("sop_number", f"%{code}%").execute()
            if kw_res.data:
                for row in kw_res.data:
                    if row['source_link'] not in seen_links:
                        db_results.append(row)
                        seen_links.add(row['source_link'])

        # B. Vector Search for concepts
        if len(db_results) < 8:
            embed = gemini_client.models.embed_content(model="models/gemini-embedding-2", contents=term)
            vec_res = supabase.rpc('match_sops', {'query_embedding': embed.embeddings[0].values, 'match_threshold': 0.25, 'match_count': 3}).execute()
            if vec_res.data:
                for row in vec_res.data:
                    if row['source_link'] not in seen_links:
                        db_results.append(row)
                        seen_links.add(row['source_link'])
    
    return db_results[:8]

# --- 6. CHAT INTERFACE ---
# Render History
for msg in st.session_state.messages:
    avatar = BOT_AVATAR if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask about stock aging, procurement, or a specific SOP..."):
    # 1. Add User message to state and UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Process Expert Response
    with st.chat_message("assistant", avatar=BOT_AVATAR):
        with st.status("Consulting the archives...", expanded=False) as status:
            results = get_expert_context(prompt)
            
            context_text = ""
            if results:
                for doc in results:
                    s_url = fix_domino_url(doc['source_link'])
                    context_text += f"\n--- SOP: {doc['sop_number']} ({doc['title']}) ---\n"
                    context_text += f"URL: {s_url}\nCONTENT: {doc['content']}\n"
                status.update(label="Information retrieved!", state="complete")
            else:
                context_text = "No direct SOP matches found."
                status.update(label="No direct matches found.", state="error")

        # Prepare payload for streaming
        chat_contents = []
        for m in st.session_state.messages[:-1]:
            role = "user" if m["role"] == "user" else "model"
            chat_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
        
        chat_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=f"CONTEXT:\n{context_text}\n\nQUESTION: {prompt}")]))

        # Stream the response to UI (Fixes duplicate bug)
        response_stream = gemini_client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=chat_contents,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.1)
        )

        full_response = st.write_stream(chunk.text for chunk in response_stream if chunk.text)
        
        # Finally, save to history after the stream finishes
        st.session_state.messages.append({"role": "assistant", "content": full_response})