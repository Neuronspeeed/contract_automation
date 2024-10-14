import asyncio
import nest_asyncio
import logging
import os
import traceback
from document_processing import process_documents, load_templates
from ai_functions import extract_pii, identify_parties, construct_contract, agent_action, determine_contract_details
from utils import verify_information
from models import PIIData, ContractParties, Contract, AgentState
from config import TEMPLATES_FOLDER

# Apply nest_asyncio to allow nested asyncio calls
nest_asyncio.apply()

# Maximum number of retries allowed during PII verification
MAX_RETRIES = 3

# Set up logging
logging.basicConfig(filename='agent_workflow.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

print(f"Current working directory: {os.getcwd()}")
print(f"Templates folder path: {os.path.abspath(TEMPLATES_FOLDER)}")

async def agent_workflow():
    templates = load_templates(TEMPLATES_FOLDER)
    documents = await process_documents()
    print("Documents processed.")

    state = AgentState()

    while True:
        action = agent_action(state)
        
        if action.action == "extract_pii":
            for doc, text in documents.items():
                pii = extract_pii(text)
                if verify_information(pii):
                    state.verified_pii_data.append(pii)
        
        elif action.action == "identify_parties":
            state.parties = identify_parties(state.verified_pii_data)
        
        elif action.action == "determine_contract_type":
            if state.contract_details and state.contract_details.contract_type:
                print(f"Contract type already determined: {state.contract_details.contract_type}")
                print(f"Roles: {state.contract_details.additional_info}")
                confirmation = input("Is this contract type and role assignment correct? (yes/no): ").lower()
                if confirmation == 'yes':
                    continue
                else:
                    state.contract_details = None

            while True:
                contract_type = input("Enter contract type (airbnb, buy-sell, it-consulting): ").lower().replace(" ", "-")
                template_filename = next((t for t in templates.keys() if contract_type in t.lower()), None)
                if template_filename:
                    state.contract_details = determine_contract_details(state.parties, contract_type)
                    print(f"Contract type: {state.contract_details.contract_type}")
                    roles = state.contract_details.additional_info
                    if roles:
                        for role, name in roles.items():
                            print(f"{role.capitalize()}: {name}")
                        confirmation = input("Is this role assignment correct? (yes/no): ").lower()
                        if confirmation == 'yes':
                            break
                        else:
                            state.contract_details = None
                    else:
                        print("Error: No roles assigned. Please try again.")
                else:
                    print(f"No template found for {contract_type}. Available templates: {', '.join(templates.keys())}")
        
        elif action.action == "construct_contract":
            if not state.contract_details:
                print("Contract details not determined yet. Please determine contract type first.")
                continue
            
            template_filename = next((t for t in templates.keys() if state.contract_details.contract_type in t.lower()), None)
            if not template_filename:
                print(f"No template found for {state.contract_details.contract_type}. Available templates: {', '.join(templates.keys())}")
                continue
            
            selected_template = templates[template_filename]['content']
            state.contract = construct_contract(state.parties, state.verified_pii_data[0].address, selected_template, state.contract_details)
        
        elif action.action == "finish":
            break
        
        else:
            print(f"Unknown action: {action.action}")
        
        print(f"Completed action: {action.action}")

    if state.contract:
        print("\nContract constructed:")
        print(f"Buyer: {state.contract.buyer}")
        print(f"Seller: {state.contract.seller}")
        print(f"Address: {state.contract.address}")
        print(f"Terms: {state.contract.terms}")
    else:
        print("No contract was constructed.")

if __name__ == "__main__":
    asyncio.run(agent_workflow())
