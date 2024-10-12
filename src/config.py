import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("No OpenAI API key found in environment variables")

DATA_FOLDER = 'data'
SYSTEM_PROMPT = """
You are an AI agent specializing in contract creation and personal information extraction. 
Your role is to guide the process of extracting information from documents, verifying it with human input, 
identifying parties, and constructing a contract. Follow the workflow precisely and ask for human input when needed.
"""
