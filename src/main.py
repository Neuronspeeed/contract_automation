import asyncio
import nest_asyncio
import logging
import os
import traceback
from document_processing import process_documents, load_templates
from ai_functions import extract_pii, identify_parties, construct_contract, agent_action, determine_contract_details
from utils import verify_information
from models import PIIData, ContractParties, Contract, AgentState, ContractDetails
from config import TEMPLATES_FOLDER
from typing import List

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

    # Extract and verify PII first
    for doc, text in documents.items():
        pii_list = await extract_pii(text)
        verified_pii_list = verify_information(pii_list)
        state.verified_pii_data.extend(verified_pii_list)

    print(f"Verified PII data: {len(state.verified_pii_data)} entries")

    while True:
        action = await agent_action(state, templates)
        
        print(f"Agent decided to: {action.action}")
        print(f"Reason: {action.reason}")
        
        if action.action == "determine_contract_type":
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

        elif action.action == "identify_parties":
            if not state.contract_details or not state.contract_details.contract_type:
                print("Contract type not determined yet. Please determine contract type first.")
                continue
            state.parties = await identify_parties(state.verified_pii_data, state.contract_details.contract_type)
            print("Parties identified:")
            for party in state.parties.parties:
                print(f"{party.role}: {party.name}")

        elif action.action == "construct_contract":
            if not state.contract_details or not state.parties:
                print("Contract details or parties not determined yet. Please complete these steps first.")
                continue
            
            template_filename = next((t for t in templates.keys() if state.contract_details.contract_type in t.lower()), None)
            if not template_filename:
                print(f"No template found for {state.contract_details.contract_type}. Available templates: {', '.join(templates.keys())}")
                continue
            
            selected_template = templates[template_filename]['content']
            state.contract = await construct_contract(state.parties, state.verified_pii_data[0].address, selected_template, state.contract_details)
            print("Contract constructed.")

        elif action.action == "finish":
            print("Contract creation process completed.")
            break
        
        else:
            print(f"Unknown action: {action.action}")
        
        print(f"Completed action: {action.action}")

    if state.contract:
        print("\nFinal Contract:")
        print(f"Parties: {', '.join([f'{party.role}: {party.name}' for party in state.contract.parties])}")
        print(f"Address: {state.contract.address}")
        print(f"Terms: {state.contract.terms}")
    else:
        print("No contract was created.")

# Run the async workflow
if __name__ == "__main__":
    asyncio.run(agent_workflow())
