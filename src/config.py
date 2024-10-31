import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
<<<<<<< Updated upstream
    raise ValueError("No OpenAI API key found in environment variables")
=======
    raise ValueError("OpenAI API key not found in environment variables")
>>>>>>> Stashed changes

DATA_FOLDER = 'data'

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
<<<<<<< Updated upstream
=======

# Add English language support
LANGUAGE = 'en'

OUTPUT_FOLDER = "output_contracts"
>>>>>>> Stashed changes
