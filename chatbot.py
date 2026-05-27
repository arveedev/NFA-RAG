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

# --- 2. THE AI PERSONA (SYSTEM PROMPT) ---
SYSTEM_INSTRUCTION = """You are the ultimate Agency Standard Operating Procedure (SOP) Expert AI.
Your personality is highly professional, exceptionally accurate, but with a witty, dry sense of humor—like a brilliant, seasoned senior government employee who knows the entire regulatory rulebook by heart and secretly enjoys showing it off.

CRITICAL RULES:
1. NO HALLUCINATIONS: You must ONLY answer based on the 'CONTEXT FROM DATABASE' provided. If a specific SOP is missing from the context block, tell the user exactly what you see in your context and politely ask them to provide more keywords.
2. MANDATORY CITATIONS: Every time you provide information, you MUST explicitly state the SOP NUMBER and provide the exact clickable [Source Link] provided in the context.
3. EXHIBITS AND FORMS: If the context includes details about exhibits, specific forms, or preferred document layouts, emphasize them so the user doesn't submit incorrect paperwork.
4. BE CONCISE AND DIRECT: Do not use unnecessary bureaucratic fluff. Give the answer immediately, then add your witty nuance."""

# --- 3. UTILITY FUNCTIONS ---
def fix_domino_url(url):
    """Patches missing Lotus Domino paths that cause 404 Design Note errors."""
    if not url:
        return url
    # If the scraped link points directly to the root domain instead of the webapp subdirectory
    if "nfaweb.nfa.gov.ph" in url and "/webapp/msd/sopweb.nsf/" not in url:
        url = url.replace("https://nfaweb.nfa.gov.ph/", "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/")
        # Remove any accidental double slashes created by the replacement
        url = re.sub(r'(?<!:)/{2,}', '/', url)
    return url

# --- 4. STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="SOP Expert AI", page_icon="🤖", layout="centered")
st.title("🤖 NFA SOP Expert AI")
st.caption("Stable Release: High-Quota Hybrid Search")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "model", 
        "content": "Hello! I am your resident SOP Expert. What procedure or obscure exhibit can I help you untangle today?"
    })

# Render conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. CORE CHATBOT ENGINE ---
if user_prompt := st.chat_input("Ask about procedures, forms, or specific codes like TS-SQ04..."):
    
    # Show User Input
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    
    # Process AI Response
    with st.chat_message("model"):
        status_text = st.empty()
        status_text.text("🔍 Scanning database via Hybrid Search...")
        
        try:
            db_results = []
            seen_links = set()
            
            # PHASE A: Exact Keyword/Code Matching
            detected_codes = re.findall(r'\b[A-Z]{2,4}-[A-Z0-9]{2,5}\b', user_prompt.upper())
            for code in detected_codes:
                keyword_response = supabase.table("sops").select("*").ilike("sop_number", f"%{code}%").execute()
                if keyword_response.data:
                    for row in keyword_response.data:
                        if row['source_link'] not in seen_links:
                            db_results.append(row)
                            seen_links.add(row['source_link'])

            # PHASE B: Vector Semantic Search
            if len(db_results) < 5:
                # We are using your EXACT original embedding model here to prevent 404s
                embed_response = gemini_client.models.embed_content(
                    model="models/gemini-embedding-2",
                    contents=user_prompt
                )
                query_vector = embed_response.embeddings[0].values
                
                vector_response = supabase.rpc(
                    'match_sops', 
                    {'query_embedding': query_vector, 'match_threshold': 0.3, 'match_count': 5}
                ).execute()
                
                if vector_response.data:
                    for row in vector_response.data:
                        if row['source_link'] not in seen_links and len(db_results) < 6:
                            db_results.append(row)
                            seen_links.add(row['source_link'])

            # Build and Sanitize Context Block
            context_text = ""
            if db_results:
                for doc in db_results:
                    sanitized_url = fix_domino_url(doc['source_link'])
                    context_text += f"\n\n--- SOP NUMBER: {doc['sop_number']} ---\n"
                    context_text += f"TITLE: {doc['title']}\n"
                    context_text += f"LINK: {sanitized_url}\n"
                    context_text += f"CONTENT:\n{doc['content']}\n"
            else:
                context_text = "No relevant SOPs or documents found matching this query in the database."

            # Construct Streaming Payload
            chat_contents = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                chat_contents.append(types.Content(role=role, parts=[types.Part.from_text(text=m["content"])]))
            
            augmented_prompt = f"CONTEXT FROM DATABASE:\n{context_text}\n\nUSER QUESTION:\n{user_prompt}"
            chat_contents.append(types.Content(role="user", parts=[types.Part.from_text(text=augmented_prompt)]))
            
            status_text.empty() # Remove loading text
            
            # Call Streaming API
            # THIS IS THE FIX: Using gemini-1.5-flash for the 1,500/day quota limit.
            response_stream = gemini_client.models.generate_content_stream(
                model='gemini-1.5-flash',
                contents=chat_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.15
                )
            )
            
            # Helper generator to pipe stream directly into Streamlit UI component
            def chunk_generator():
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text

            # Stream chunks smoothly onto the page
            full_response = st.write_stream(chunk_generator())
            st.session_state.messages.append({"role": "model", "content": full_response})
            
        except Exception as e:
            status_text.empty()
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                st.warning("⚠️ *I am answering questions a bit too fast and hit a temporary speed limit. Please wait 10 seconds and try again.*")
            else:
                st.error(f"System Error: {e}")