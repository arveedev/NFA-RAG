import os
import time
import re
from playwright.sync_api import sync_playwright
from supabase import create_client
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Setup
load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

CATEGORY_URLS = [
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Expand=2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.1.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.1.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.1.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.1.21&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.2.2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=1000&Collapse=1.2.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.2.4.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.2.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.2.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.2.9&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.3.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1&Count=30&Collapse=1.3.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.28&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.29&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.32&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.38&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.39&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.40&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.26&Count=30&Collapse=1.3.43&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=1.3.57&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=1.3.65&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=1.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=1.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=1.5.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.1.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.1.6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.1.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=1.3.55&Count=30&Collapse=2.3.11&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.21&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.22&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.23&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.27&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.3.28&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.3.14&Count=30&Collapse=2.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=2.4.6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.2.10&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.3.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.3.9&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.3.15&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.4.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.4.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=2.4.6&Count=30&Collapse=3.4.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=3.4.23&Count=30&Collapse=3.4.24&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=3.4.23&Count=30&Collapse=3.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisFA?OpenPage&Start=3.4.23&Count=30&Collapse=3.5.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.1.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.2.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=1.3.15&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.22&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.23&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.32&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.33&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.34&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.3.35&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.3.21&Count=25&Collapse=1.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.4.15&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.4.16&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.4.19&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.4.21&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.4.9&Count=25&Collapse=1.5.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.5.5&Count=25&Collapse=1.6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.5.5&Count=25&Collapse=1.6.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.5.5&Count=25&Collapse=1.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.5.5&Count=25&Collapse=1.7.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.7.21&Count=25&Collapse=1.7.23&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.7.21&Count=25&Collapse=1.7.32&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.7.21&Count=25&Collapse=1.7.33&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.7.21&Count=25&Collapse=1.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.7.21&Count=25&Collapse=1.8.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.9&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.10&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.13&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.13.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=1.8.17&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1.8.4.2&Count=25&Collapse=2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.2.12&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.4.6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=2.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=2.2&Count=25&Collapse=3.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=3.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=4.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=4.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisTSS?OpenPage&Start=1&Count=25&Collapse=4.2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=1.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=2.1.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=2.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisSSS?OpenPage&Start=1&Count=25&Collapse=2.3.4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/MisOther?OpenPage&Start=1&Count=25&Collapse=1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.1.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.1.1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.2.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Superseded?OpenPage&Start=1&Count=25&Collapse=1.1.2.2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.14&Count=15&Collapse=1.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.14&Count=15&Collapse=1.18&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.14&Count=15&Collapse=1.22&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.28&Count=15&Collapse=1.30&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.28&Count=15&Collapse=1.36&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.42&Count=15&Collapse=1.43&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.42&Count=15&Collapse=1.45&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.42&Count=15&Collapse=1.47&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.55&Count=15&Collapse=1.55&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.68&Count=15&Collapse=1.75&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.82&Count=15&Collapse=1.83&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.82&Count=15&Collapse=1.87&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.82&Count=15&Collapse=1.89&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.102&Count=15&Collapse=1.103&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.102&Count=15&Collapse=1.104&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.102&Count=15&Collapse=1.107&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.102&Count=15&Collapse=1.108&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.102&Count=15&Collapse=1.110&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.135&Count=15&Collapse=1.138&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.145&Count=15&Collapse=1.146&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.157&Count=15&Collapse=1.162&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.157&Count=15&Collapse=1.163&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.157&Count=15&Collapse=1.165&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.171&Count=15&Collapse=1.172&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.183&Count=15&Collapse=1.189&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.189.8&Count=15&Collapse=1.191&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.189.8&Count=15&Collapse=1.192&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.189.8&Count=15&Collapse=1.193&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.189.8&Count=15&Collapse=1.195&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.197&Count=15&Collapse=1.202&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.197&Count=15&Collapse=1.203&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.197&Count=15&Collapse=1.203.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.214&Count=15&Collapse=1.218&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.225&Count=15&Collapse=1.225&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=1.225&Count=15&Collapse=1.227&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=2.19&Count=15&Collapse=2.22&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=2.19&Count=15&Collapse=2.24&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=2.19&Count=15&Collapse=2.24.3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=3.8&Count=15&Collapse=3.14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=5.13&Count=15&Collapse=6.5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.5.1&Count=15&Collapse=6.8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.30&Count=15&Collapse=6.41&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.41.3&Count=15&Collapse=6.43&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.51&Count=15&Collapse=6.51&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.51&Count=15&Collapse=6.52&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.51&Count=15&Collapse=6.57&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.51&Count=15&Collapse=6.61&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.68&Count=15&Collapse=6.77&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.82&Count=15&Collapse=6.83&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.82&Count=15&Collapse=6.86&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.93&Count=15&Collapse=6.95&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.105&Count=15&Collapse=6.107&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.105&Count=15&Collapse=6.113&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.119&Count=15&Collapse=6.120&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.119&Count=15&Collapse=6.121&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.119&Count=15&Collapse=6.122&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.119&Count=15&Collapse=6.125&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.119&Count=15&Collapse=6.128&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.133&Count=15&Collapse=6.134&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.133&Count=15&Collapse=6.138&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.133&Count=15&Collapse=6.138.1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.133&Count=15&Collapse=6.139&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.133&Count=15&Collapse=6.140&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.147&Count=15&Collapse=6.151&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.147&Count=15&Collapse=6.153&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.147&Count=15&Collapse=6.159&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.162&Count=15&Collapse=6.163&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.162&Count=15&Collapse=6.166&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.162&Count=15&Collapse=6.168&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=6.175&Count=15&Collapse=6.178&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Amended?OpenPage&Start=7.10&Count=15&Collapse=7.15&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=1&Count=25&Collapse=1&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=1&Count=25&Collapse=2&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=1&Count=25&Collapse=3&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=3.2&Count=25&Collapse=4&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=3.2&Count=25&Collapse=5&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=3.2&Count=25&Collapse=6&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=3.2&Count=25&Collapse=7&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=3.2&Count=25&Collapse=8&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=8.4&Count=25&Collapse=9&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=8.4&Count=25&Collapse=10&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=8.4&Count=25&Collapse=11&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=8.4&Count=25&Collapse=12&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=12.4&Count=25&Collapse=13&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=12.4&Count=25&Collapse=14&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=12.4&Count=25&Collapse=15&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=15.4&Count=25&Collapse=16&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=15.4&Count=25&Collapse=17&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=15.4&Count=25&Collapse=18&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=15.4&Count=25&Collapse=19&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=19.1&Count=25&Collapse=20&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=19.1&Count=25&Collapse=21&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=22&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=23&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=24&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=25&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=26&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=21.6&Count=25&Collapse=27&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=27.3&Count=25&Collapse=28&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=27.3&Count=25&Collapse=29&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=27.3&Count=25&Collapse=30&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=27.3&Count=25&Collapse=31&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=32&Count=25&Expand=32&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=32&Count=25&Collapse=32&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=32&Count=25&Collapse=33&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=32&Count=25&Collapse=34&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=32&Count=25&Collapse=35&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=35.2&Count=25&Collapse=36&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=35.2&Count=25&Collapse=37&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=35.2&Count=25&Collapse=38&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=35.2&Count=25&Collapse=39&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=35.2&Count=25&Collapse=40&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=40.5&Count=25&Collapse=41&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=40.5&Count=25&Collapse=42&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=40.5&Count=25&Collapse=43&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=43.4&Count=25&Collapse=44&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=43.4&Count=25&Collapse=45&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=43.4&Count=25&Collapse=46&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=43.4&Count=25&Collapse=47&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=43.4&Count=25&Collapse=47&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=48.1&Count=25&Collapse=49&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=48.1&Count=25&Collapse=50&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=48.1&Count=25&Collapse=51&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=51.8&Count=25&Collapse=52&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=51.8&Count=25&Collapse=53&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=51.8&Count=25&Collapse=54&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=54.1&Count=25&Collapse=55&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=54.1&Count=25&Collapse=56&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=57&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=58&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=59&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=60&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=61&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=57&Count=25&Collapse=62&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=62.6&Count=25&Collapse=63&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=62.6&Count=25&Collapse=64&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=62.6&Count=25&Collapse=65&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=62.6&Count=25&Collapse=66&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=66.11&Count=25&Collapse=67&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=66.11&Count=25&Collapse=68&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=66.11&Count=25&Collapse=69&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=66.11&Count=25&Collapse=70&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=71&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=72&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=73&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=74&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=75&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=76&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=70.5&Count=25&Collapse=77&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=77.2&Count=25&Collapse=78&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=77.2&Count=25&Collapse=79&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=77.2&Count=25&Collapse=80&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=80.6&Count=25&Collapse=81&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=80.6&Count=25&Collapse=82&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=80.6&Count=25&Collapse=83&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=80.6&Count=25&Collapse=84&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=80.6&Count=25&Collapse=85&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=86&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=87&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=88&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=89&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=90&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=85.12&Count=25&Collapse=91&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=92&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=93&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=94&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=95&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=96&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=97&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=98&AutoFramed",
    'https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=99&AutoFramed',
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=100&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=101&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=91.16&Count=25&Collapse=102&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=116&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=117&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=118&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=119&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=120&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=121&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=122&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=123&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=115&Count=25&Collapse=124&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=140&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=141&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=142&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=143&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=144&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=139&Count=25&Collapse=145&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=164&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=165&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=166&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=167&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=168&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=169&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=170&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=171&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=172&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=163&Count=25&Collapse=173&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=188&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=189&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=190&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=191&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=192&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=193&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=194&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=187&Count=25&Collapse=195&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=212&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=213&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=214&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=215&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=216&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=217&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=218&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=219&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=220&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=221&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=223&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=222&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=224&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=225&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=226&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=227&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=228&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=229&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=230&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=211&Count=25&Collapse=231&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=232&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=233&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=234&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=235&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=236&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=237&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=238&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=239&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=231.4&Count=25&Collapse=240&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=241&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=242&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=243&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=244&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=245&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=246&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=247&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=248&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=240.14&Count=25&Collapse=249&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=25&Collapse=250&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=25&Collapse=251&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=25&Collapse=252&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=25&Collapse=253&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=25&Collapse=254&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Exhibits?OpenPage&Start=249.15&Count=2500&Collapse=255&AutoFramed",
    "https://nfaweb.nfa.gov.ph/webapp/msd/sopweb.nsf/Definition?OpenPage"
]

def get_embedding(text, max_retries=5):
    """Generates embeddings with exponential backoff for 429 API errors."""
    base_delay = 4
    
    for attempt in range(max_retries):
        try:
            response = gemini_client.models.embed_content(
                model="models/gemini-embedding-2",
                contents=text[:8000]
            )
            if response and response.embeddings:
                return response.embeddings[0].values
            else:
                print(f"  ❌ No embeddings returned from API")
                return None
            
        except Exception as e:
            error_msg = str(e).lower()
            if "429" in error_msg or "resource_exhausted" in error_msg:
                if attempt == max_retries - 1:
                    print(f"  ❌ Max retries reached. Skipping this embedding.")
                    return None
                    
                wait_time = base_delay * (2 ** attempt)
                print(f"  ⚠️ Rate limit hit. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Embedding error: {e}")
                return None

def process_sop(page, sop_url):
    print(f"\n  -> Loading SOP: {sop_url}")
    page.goto(sop_url, timeout=60000)
    
    content_text = page.locator("body").inner_text()
    
    # Extract SOP Number and Title
    sop_match = re.search(r"SOP NO:?\s*([A-Za-z0-9\-]+)", content_text, re.IGNORECASE)
    title_match = re.search(r"Title:?\s*(.*)", content_text, re.IGNORECASE)
    
    sop_num = sop_match.group(1).strip() if sop_match else "UNKNOWN"
    title = title_match.group(1).strip() if title_match else "Untitled SOP"
    
    print(f"  -> Found {sop_num}: {title}")
    
    # Save to Supabase
    embedding = get_embedding(content_text)
    if embedding:
        supabase.table("sops").insert({
            "sop_number": sop_num,
            "title": title,
            "source_link": sop_url,
            "content": content_text,
            "embedding": embedding
        }).execute()
        print(f"  ✅ Saved {sop_num} to database.")

def main():
    print("Fetching existing records from database to prevent duplicate processing...")
    try:
        # Fetch only the URLs to create a fast lookup set
        response = supabase.table("sops").select("source_link").execute()
        existing_links = set()
        if response.data:
            for row in response.data:
                if isinstance(row, dict) and "source_link" in row:
                    link = row.get("source_link")
                    if isinstance(link, str):
                        existing_links.add(link)
        print(f"Loaded {len(existing_links)} existing SOP URLs.")
    except Exception as e:
        print(f"Failed to load existing links: {e}")
        existing_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        doc_processor_page = browser.new_page()
        list_page = browser.new_page()
        
        unique_sop_links = set()
        
        # 1. Harvest links from all provided category URLs
        for category_url in CATEGORY_URLS:
            print(f"\nScanning Category: {category_url}")
            try:
                list_page.goto(category_url)
                list_page.wait_for_timeout(4000) # Give frames time to load
                
                links_found_in_category = 0
                for frame in list_page.frames:
                    links = frame.locator("a[href*='?OpenDocument']").all()
                    for link in links:
                        href = link.get_attribute("href")
                        if href:
                            full_url = href if href.startswith("http") else f"https://nfaweb.nfa.gov.ph{href}"
                            unique_sop_links.add(full_url)
                            links_found_in_category += 1
                        
                print(f"Found {links_found_in_category} document links in this category.")
            except Exception as e:
                print(f"Failed to load category {category_url}: {e}")

        print(f"\n--- Harvesting Phase Complete ---")
        print(f"Total Unique SOPs to evaluate: {len(unique_sop_links)}\n")
        
        # 2. Process all harvested links
        for link in unique_sop_links:
            # CHECK CACHE FIRST: Skip Playwright and Gemini completely if we already have it
            if link in existing_links:
                print(f"  ⏩ Skipped (Already in DB): {link}")
                continue
                
            try:
                process_sop(doc_processor_page, link)
                # Baseline throttle to ensure we don't naturally exceed 15 RPM
                time.sleep(4) 
            except Exception as e:
                print(f"Failed to process {link}: {e}")
        
        browser.close()
        print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()