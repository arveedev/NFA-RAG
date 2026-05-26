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
SYSTEM_INSTRUCTION = """You are the ultimate Agency Standard Operating Procedure (SOP) Expert AI.
Your personality is highly professional, exceptionally accurate, but with a witty, dry sense of humor.

CRITICAL RULES:
1. NO HALLUCINATIONS: You must ONLY answer based on the 'CONTEXT FROM DATABASE' provided. If a specific SOP is missing, state exactly what you see and ask for more keywords.
2. MANDATORY CITATIONS: Every time you provide information, you MUST explicitly state the SOP NUMBER and provide the clickable [Source Link].
3. EXHIBITS AND FORMS: Emphasize specific forms or document layouts mentioned in the context.
4. BE CONCISE AND DIRECT: Give the answer immediately, then add your witty nuance."""

# --- 3. UTILITY FUNCTIONS ---
def fix_domino_url(url):
    """Patches missing Lotus Domino paths."""
    if not url: return url
    if "nfaweb.nfa.gov.ph" in url and "/webapp/msd/sopweb.nsf/" not in url:
        url = url.replace("https://nfaweb.nfa.gov.ph/", "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/")
        url = re.sub(r'(?<!:)/{2,}', '/', url)
    return url

# --- 4. STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="NFA SOP Expert", page_icon="🤖", layout="centered")

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
st.caption("Restored Hybrid Search (V2.5 - Fixed Resource Routing)")

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello! I am your resident SOP Expert. What procedure or obscure exhibit can I help you untangle today?"
    })

# Render conversation history
for msg in st.session_state.messages:
    avatar = BOT_AVATAR if msg["role"] == "model" else None
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# --- 5. CORE CHATBOT ENGINE ---
if user_prompt := st.chat_input("Ask about procedures, forms, or specific codes like TS-SQ04..."):
    
    # Show User Input
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)
    
    # Process AI Response
    with st.chat_message("model", avatar=BOT_AVATAR):
        status_placeholder = st.empty()
        status_placeholder.text("🔍 Scanning database...")
        
        try:
            db_results = []
            seen_links = set()
            
            # PHASE A: Exact Keyword/Code Matching
            detected_codes = re.findall(r'\b[A-Z]{2,4}-[A-Z0-9]{2,5}\b', user_prompt.upper())
            for code in detected_codes:
                kw_res = supabase.table("sops").select("*").ilike("sop_number", f"%{code}%").execute()
                if kw_res.data:
                    for row in kw_res.data:
                        if row['source_link'] not in seen_links:
                            db_results.append(row)
                            seen_links.add(row['source_link'])

            # PHASE B: Vector Semantic Search
            if len(db_results) < 5:
                # FIX 1: Removed 'models/' prefix
                embed_resp = gemini_client.models.embed_content(
                    model="text-embedding-004",
                    contents=user_prompt
                )
                query_vector = embed_resp.embeddings[0].values
                
                vec_res = supabase.rpc(
                    'match_sops', 
                    {'query_embedding': query_vector, 'match_threshold': 0.15, 'match_count': 5}
                ).execute()
                
                if vec_res.data:
                    for row in vec_res.data:
                        if row['source_link'] not in seen_links and len(db_results) < 6:
                            db_results.append(row)
                            seen_links.add(row['source_link'])

            # Build Context Block
            context_text = ""
            if db_results:
                for doc in db_results:
                    sanitized_url = fix_domino_url(doc['source_link'])
                    context_text += f"\n\n--- SOP NUMBER: {doc['sop_number']} ---\n"
                    context_text += f"TITLE: {doc['title']}\n"
                    context_text += f"LINK: {sanitized_url}\n"
                    context_text += f"CONTENT:\n{doc['content']}\n"
            else:
                context_text = "No relevant SOPs found in the database for this query."

            # Construct History for the model
            chat_contents = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                chat_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
            
            augmented_prompt = f"CONTEXT FROM DATABASE:\n{context_text}\n\nUSER QUESTION:\n{user_prompt}"
            chat_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=augmented_prompt)]))
            
            status_placeholder.empty()
            
            # FIX 2: Switched to universal 'gemini-1.5-flash'
            response_stream = gemini_client.models.generate_content_stream(
                model='gemini-1.5-flash',
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1
                )
            )
            
            full_response = st.write_stream(chunk.text for chunk in response_stream if chunk.text)
            st.session_state.messages.append({"role": "model", "content": full_response})
            
        except Exception as e:
            status_placeholder.empty()
            st.error(f"System Error: {e}")