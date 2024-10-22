import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("Nu s-a găsit cheia API OpenAI în variabilele de mediu")

DATA_FOLDER = 'data'

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Add Romanian language support
LANGUAGE = 'ro'
