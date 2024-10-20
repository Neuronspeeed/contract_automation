import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')
if not API_KEY:
    raise ValueError("No OpenAI API key found in environment variables")

DATA_FOLDER = 'data'

# System prompt for the agent
SYSTEM_PROMPT = """
You are an AI assistant specialized in contract automation. Your task is to guide the process of extracting information, identifying parties, and constructing contracts based on the available data and templates.

Follow these guidelines:

1. PII Extraction:
   Extract names, addresses, and any other relevant personal details from the provided documents.

2. Party Identification:
   For each contract type, ask witch role each person should have in the contract:
   - Buy-sell contract: Identify the buyer and the seller.
   - Airbnb contract: Identify the landlord (property owner) and the tenant (guest).
   - IT contract: Identify the IT consultant and the client.

3. Contract Construction:
   - Insert party names directly into the contract without brackets.
   - Use the provided addresses accurately in the appropriate fields.
   - Ensure all placeholders in contract templates are replaced with the correct information.
"""

PII_EXTRACTION_PROMPT = "Extract personal identifiable information (PII) from documents."

PARTY_IDENTIFICATION_PROMPT = """
For a {contract_type} contract, assign roles to the following parties:

{pii_text}

Your task is to determine the roles of each person in the context of a {contract_type} contract.
Consider the guidelines provided in the system prompt.

For each person, provide their name and ask the human if person witch role they should have in the contract.
"""

CONTRACT_CONSTRUCTION_PROMPT = """Construct a {contract_type} contract using the following template and information:

Template:
{template}

Parties: {parties_info}
Address: {address}
Additional Details: {additional_info}

Instructions:
1. Use the provided template as a base for the contract.
2. Insert the parties' names directly into the contract without brackets.
3. Use the provided address for the 'Address' field in the contract.
4. Ensure all placeholders in the template are replaced with appropriate information.
5. If any information is missing, leave the corresponding field blank or use a placeholder like [To be determined].
"""

TEMPLATES_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')