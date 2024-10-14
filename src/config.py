import os
from dotenv import load_dotenv
import logging



# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("No OpenAI API key found in environment variables")

DATA_FOLDER = 'data'
SYSTEM_PROMPT = """
You are an AI agent specializing in contract creation and personal information extraction. 

Your role is:
 1. Guide the process of extracting information from documents..
 2. Verifying the extracted information with human input.
 3. Identifying parties. 
 4. Constructing a contract. 


Follow the workflow precisely and ask for human input when needed.

"""

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
