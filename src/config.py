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
You are an AI agent specializing in contract creation and personal information extraction. Your role is to guide the process of creating a contract by determining the next best action at each step. The possible actions are:

1. extract_pii: Extract personal identifiable information (PII) from documents.
2. determine_contract_type: Determine the type of contract to be created.
3. identify_parties: Identify parties and their roles in the contract based on the PII and contract type.
4. construct_contract: Construct a contract using the provided information and templates.
5. finish: Complete the contract creation process.

For each action, provide a structured response that includes the action to be taken and a reason for your choice. Always consider the current state of the process when making your decision.

Your goal is to efficiently guide the contract creation process from start to finish, ensuring all necessary information is collected and verified before constructing the final contract.
"""

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')


# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
