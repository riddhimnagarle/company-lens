import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load the secret API key from your .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    print("[ERROR] GEMINI_API_KEY is empty in your .env file!")
    print("Please open .env and paste your key after GEMINI_API_KEY=")
    exit(1)

print("[OK] API Key detected successfully!")
print("[INFO] Calling Google Gemini to verify connection...")

# 2. Connect to the Gemini model
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=api_key
    )
    response = llm.invoke("Say 'CompanyLens is officially online and ready to build!' in one short sentence.")
    
    # Handle response content whether string or list
    reply_text = response.content
    if isinstance(reply_text, list) and len(reply_text) > 0:
        if isinstance(reply_text[0], dict) and "text" in reply_text[0]:
            reply_text = reply_text[0]["text"]
        elif hasattr(reply_text[0], "text"):
            reply_text = reply_text[0].text

    print("\n--- AI Response ---")
    print(reply_text)
    print("-------------------")
    print("[SUCCESS] Your environment, API key, and LangChain are working perfectly!")
except Exception as e:
    print(f"[ERROR] connecting to Gemini: {e}")



