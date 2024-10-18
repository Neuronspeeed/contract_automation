import asyncio
import nest_asyncio
import logging
import os
import traceback
from document_processing import process_documents, load_templates
from ai_functions import extract_pii, identify_parties, construct_contract, determine_contract_details
from utils import verify_information
from models import PIIData, ContractParties, Contract, AgentState, ContractDetails, ContractParty
from config import TEMPLATES_FOLDER
from typing import List, Dict

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

async def determine_contract_type(state: AgentState, templates: Dict[str, Dict]) -> None:
    """
    Determine the contract type based on user input.
    
    Args:
        state (AgentState): The current state of the agent.
        templates (Dict[str, Dict]): The loaded contract templates.
    """
    print("Available contract types:")
    for template in templates.keys():
        print(f"- {template.split('.')[0]}")
    
    while True:
        contract_type = input("Enter the desired contract type: ").lower().replace(" ", "-")
        template_filename = next((t for t in templates.keys() if contract_type in t.lower()), None)
        if template_filename:
            contract_type = template_filename.split('.')[0]
            state.contract_details = ContractDetails(contract_type=contract_type, additional_info={})
            print(f"Contract type set to: {state.contract_details.contract_type}")
            break
        else:
            print(f"No template found for {contract_type}. Please choose from the available types.")

async def identify_contract_parties(state: AgentState) -> None:
    """
    Identify the parties involved in the contract with human input.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if not state.contract_details or not state.contract_details.contract_type:
        print("Contract type not determined yet. Please determine contract type first.")
        return
    
    contract_type = state.contract_details.contract_type
    role_options = {
        "buy-sell": ["buyer", "seller"],
        "airbnb": ["landlord", "tenant"],
        "it": ["IT consultant", "client"]
    }
    
    if contract_type not in role_options:
        print(f"Unsupported contract type: {contract_type}")
        return
    
    final_parties = []
    for pii in state.verified_pii_data:
        print(f"\nFor {pii.name}:")
        print("Available roles:")
        for i, role in enumerate(role_options[contract_type], 1):
            print(f"{i}. {role}")
        
        while True:
            choice = input(f"Enter the number or name for {pii.name}'s role: ").strip().lower()
            if choice.isdigit() and 1 <= int(choice) <= len(role_options[contract_type]):
                user_role = role_options[contract_type][int(choice) - 1]
                break
            elif choice in [role.lower() for role in role_options[contract_type]]:
                user_role = next(role for role in role_options[contract_type] if role.lower() == choice)
                break
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(role_options[contract_type])} or one of the role names.")
        
        final_parties.append(ContractParty(name=pii.name, roles=[user_role]))
    
    state.parties = ContractParties(parties=final_parties)
    print("\nFinal Parties identified:")
    for party in state.parties.parties:
        print(f"{', '.join(party.roles)}: {party.name}")

async def construct_final_contract(state: AgentState, templates: Dict[str, Dict]) -> None:
    """
    Construct the final contract based on the determined details and parties.
    
    Args:
        state (AgentState): The current state of the agent.
        templates (Dict[str, Dict]): The loaded contract templates.
    """
    if not state.contract_details or not state.parties:
        print("Contract details or parties not determined yet. Please complete these steps first.")
        return
    
    template_filename = next((t for t in templates.keys() if state.contract_details.contract_type in t.lower()), None)
    if not template_filename:
        print(f"No template found for {state.contract_details.contract_type}. Available templates: {', '.join(templates.keys())}")
        return
    
    selected_template = templates[template_filename]['content']
    address = state.verified_pii_data[0].address if state.verified_pii_data else "Address not provided"
    state.contract = await construct_contract(state.parties, address, selected_template, state.contract_details)
    print("Contract constructed.")

async def agent_workflow() -> None:
    """
    Main agent workflow for processing documents and constructing a contract.
    """
    templates = load_templates(TEMPLATES_FOLDER)
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
    await construct_final_contract(state, templates)

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
