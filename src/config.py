import os
from dotenv import load_dotenv
from openai import OpenAI
import easyocr

# Use the current working directory as the base directory
base_dir = os.getcwd()

# If your .env is one level up from the current directory, use this:
dotenv_path = os.path.join(base_dir, '../.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path)

# Get the API key from the environment variables
api_key = os.getenv('OPENAI_API_KEY')

if api_key is None:
    raise ValueError("Environment variable 'OPENAI_API_KEY' is not set. Please check your .env file.")

client = OpenAI(api_key=api_key)

# System prompt for consistency across nodes
system_prompt = (
    "You are an AI legal assistant specializing in contract creation and personal information extraction. "
    "Your role is to ensure all responses are formatted clearly, focusing on accuracy, privacy, and legality. "
    "Always ask clarifying questions if any information is incomplete or unclear. Respond concisely and use formal language appropriate for legal contexts."
    "Include all relevant details explicitly and structure output for easy readability."
)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en', 'ro'])

DATA_FOLDER = 'data'