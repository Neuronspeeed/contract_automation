import os
from dotenv import load_dotenv
from openai import OpenAI
from langgraph.graph import StateGraph, END
from typing import List

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

DATA_FOLDER = os.environ.get('DATA_FOLDER', 'data')

client = OpenAI(api_key=OPENAI_API_KEY)

def get_documents() -> List[str]:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    all_files = os.listdir(DATA_FOLDER)
    documents = [
        os.path.join(DATA_FOLDER, f) 
        for f in all_files 
        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt'))
    ]
    print(f"Total files in {DATA_FOLDER}: {len(all_files)}")
    if all_files:
        print(f"Files found: {all_files}")
        print(f"Documents to process: {len(documents)}")
        if not documents:
            print("Warning: No files with supported extensions (.pdf, .jpg, .jpeg, .png, .txt) found.")
    else:
        print(f"The {DATA_FOLDER} folder is empty.")
    return documents
