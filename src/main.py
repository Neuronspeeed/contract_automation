import asyncio
import nest_asyncio
import logging
import os
import traceback
from document_processing import process_documents, load_templates
from ai_functions import extract_pii, identify_parties, construct_contract, determine_contract_details, determine_contract_type
from utils import verify_information
from models import PIIData, ContractParties, Contract, AgentState, ContractDetails, ContractParty
from config import TEMPLATES_FOLDER
from typing import List, Dict
from template_manager import TemplateManager

# Apply nest_asyncio to allow nested asyncio calls
nest_asyncio.apply()

# Maximum number of retries allowed during PII verification
MAX_RETRIES = 3

# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

print(f"Current working directory: {os.getcwd()}")
print(f"Templates folder path: {os.path.abspath(TEMPLATES_FOLDER)}")

async def process_pii_extraction(state: AgentState, documents: Dict[str, str]) -> None:
    """
    Extract and verify PII from documents.
    
    Args:
        state (AgentState): The current state of the agent.
        documents (Dict[str, str]): The processed documents.
    """
    verified_pii_data = []
    for doc, text in documents.items():
        pii_list: List[PIIData] = await extract_pii(text)
        verified_pii_list: List[PIIData] = verify_information(pii_list)
        verified_pii_data.extend(verified_pii_list)
    
    state.verified_pii_data = verified_pii_data
    print(f"Verified PII data: {len(state.verified_pii_data)} entries")


# Determine the contract type based on PII data and available templates.
async def determine_contract_type(state: AgentState, templates: Dict[str, Dict]) -> None:
    """
    Determine the contract type based on PII data and available templates.
    
    Args:
        state (AgentState): The current state of the agent.
        templates (Dict[str, Dict]): The loaded contract templates.
    """
    available_templates = [template.split('.')[0] for template in templates.keys()]
    contract_type = await ai_functions.determine_contract_type(state.verified_pii_data, available_templates)
    
    state.contract_details = ContractDetails(contract_type=contract_type, additional_info={})
    print(f"Contract type determined: {state.contract_details.contract_type}")

# Identify the parties involved in the contract using AI.
async def identify_contract_parties(state: AgentState) -> None:
    """
    Identify the parties involved in the contract using AI.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if not state.contract_details or not state.contract_details.contract_type:
        print("Contract type not determined yet. Please determine contract type first.")
        return
    
    state.parties = await ai_functions.identify_parties(state.verified_pii_data, state.contract_details.contract_type)
    print("\nParties identified:")
    for party in state.parties.parties:
        print(f"{', '.join(party.roles)}: {party.name}")

# Construct the final contract based on the determined details and parties.
async def construct_final_contract(state: AgentState, template_manager: TemplateManager) -> None:
    """
    Construct the final contract based on the determined details and parties.
    
    Args:
        state (AgentState): The current state of the agent.
        template_manager (TemplateManager): The template manager instance.
    """
    if not state.contract_details or not state.parties:
        print("Contract details or parties not determined yet. Please complete these steps first.")
        return
    
    selected_template = template_manager.get_template(state.contract_details.contract_type)
    if not selected_template:
        print(f"No template found for {state.contract_details.contract_type}. Available templates: {', '.join(template_manager.list_available_templates())}")
        return
    
    address = state.verified_pii_data[0].address if state.verified_pii_data else "Address not provided"
    state.contract = await ai_functions.construct_contract(state.parties, address, selected_template, state.contract_details)
    print("Contract constructed.")

# Main agent workflow for processing documents and constructing a contract.
async def agent_workflow() -> None:
    """
    Main agent workflow for processing documents and constructing a contract.
    """
    templates = load_templates(TEMPLATES_FOLDER)
    template_manager = TemplateManager(templates)
    documents = await process_documents()
    print("Documents processed.")

    state = AgentState()

    # Stage 1: Document Processing and PII Extraction
    await process_pii_extraction(state, documents)

    # Stage 2: Determine contract type
    await determine_contract_type(state, templates)

    # Stage 3: Identify parties
    await identify_contract_parties(state)

    # Stage 4: Construct the contract
    await construct_final_contract(state, template_manager)

    # Finalize contract output
    if state.contract:
        print("\nFinal Contract:")
        print(f"Parties: {', '.join([f'{", ".join(party.roles)}: {party.name}' for party in state.contract.parties])}")
        print(f"Address: {state.contract.address}")
        print(f"Terms: {state.contract.terms}")
    else:
        print("No contract was created.")

# Run the async workflow
if __name__ == "__main__":
    asyncio.run(agent_workflow())
