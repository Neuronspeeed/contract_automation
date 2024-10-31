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
import ai_functions
from prompts import SYSTEM_PROMPT 

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
        for pii in pii_list:
            print("Please verify the following information:")
            print(f"Name: {pii.name}")
            print(f"Address: {pii.address}")
            is_correct = input("Is this information correct? (yes/no): ").lower()
            if is_correct == 'yes':
                verified_pii_data.append(pii)
            else:
                name = input("Please provide the correct name: ")
                address = input("Please provide the correct address: ")
                verified_pii_data.append(PIIData(name=name, address=address))
    
    state.verified_pii_data = verified_pii_data
    print(f"Verified PII data: {len(state.verified_pii_data)} entries")

async def determine_contract_type(state: AgentState, templates: Dict[str, Dict]) -> None:
    """
    Allow the user to choose the contract type based on available templates.
    
    Args:
        state (AgentState): The current state of the agent.
        templates (Dict[str, Dict]): The loaded contract templates.
    """
    available_templates = list(templates.keys())
    print("\nAvailable contract types:")
<<<<<<< Updated upstream
    for i, template in enumerate(available_templates, 1):
        print(f"{i}. {template.split('.')[0]}")
    
    while True:
        choice = input(f"\nPlease choose a contract type (1-{len(available_templates)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(available_templates):
            selected_template = available_templates[int(choice) - 1]
            contract_type = selected_template.split('.')[0]
            state.contract_details = ContractDetails(contract_type=contract_type, additional_info={})
            print(f"\nContract type selected: {state.contract_details.contract_type}")
            break
        else:
            print(f"Invalid choice. Please enter a number between 1 and {len(available_templates)}.")
=======
    print("1. airbnb")
    print("2. buy-sell")
    print("3. it")

    while True:
        contract_type = input("Please choose a contract type (1-3): ")
        if contract_type in ["1", "2", "3"]:
            contract_type = {"1": "airbnb", "2": "buy-sell", "3": "it"}.get(contract_type)
            state.contract_details = ContractDetails(contract_type=contract_type, additional_info={})
            print(f"\nSelected contract type: {state.contract_details.contract_type}")
            break
        else:
            print(f"Invalid choice. Please enter a number between 1 and 3.")
>>>>>>> Stashed changes

async def identify_contract_parties(state: AgentState) -> None:
    """
    Identify the parties involved in the contract using AI.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if not state.contract_details or not state.contract_details.contract_type:
<<<<<<< Updated upstream
        print("Contract type not determined yet. Please determine contract type first.")
        return
    
    state.parties = await ai_functions.identify_parties(state.verified_pii_data, state.contract_details.contract_type)
    print("\nParties identified:")
    for party in state.parties.parties:
        print(f"{', '.join(party.roles)}: {party.name}")

# Construct the final contract based on the determined details and parties.
async def construct_final_contract(state: AgentState, template_manager: TemplateManager) -> None:
=======
        print("Contract type has not been determined yet. Please determine the contract type first.")
        return
    
    state.parties = await ai_functions.identify_parties(state.verified_pii_data, state.contract_details.contract_type)
    print("\nIdentified parties:")
    for party in state.parties.parties:
        print(f"{', '.join(party.roles)}: {party.name}")

async def construct_final_contract(state: AgentState, template_manager: TemplateManager) -> str:
>>>>>>> Stashed changes
    """
    Construct the final contract based on the determined details and parties.
    
    Args:
        state (AgentState): The current state of the agent.
        template_manager (TemplateManager): The template manager instance.
    """
    if not state.contract_details or not state.parties:
<<<<<<< Updated upstream
        print("Contract details or parties not determined yet. Please complete these steps first.")
        return
=======
        print("Contract details or parties have not been determined yet. Please complete these steps first.")
        return None
>>>>>>> Stashed changes
    
    contract_type = state.contract_details.contract_type
    address = state.verified_pii_data[0].address if state.verified_pii_data else "Address not provided"
    additional_info = state.contract_details.additional_info
    
    template = template_manager.get_template(contract_type)
    
    try:
        state.contract = await ai_functions.construct_contract(
            contract_type=contract_type,
            parties=state.parties,
            address=address,
            additional_info=additional_info,
            template=template
        )
        print("Contract constructed.")
<<<<<<< Updated upstream
    except Exception as e:
        print(f"Error constructing contract: {str(e)}")
=======
        
        # Create output folder if it doesn't exist
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{contract_type}_{timestamp}.txt"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        
        # Save the contract to a file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(state.contract.content)
        
        print(f"Contract has been saved to: {filepath}")
    except Exception as e:
        print(f"Error constructing contract: {str(e)}")
    return filepath

async def collect_payment_details(state: AgentState) -> None:
    """
    Collect payment details for buy-sell contracts.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if state.contract_details.contract_type != "buy-sell":
        return

    print("\nPlease enter payment details:")
    
    advance = input("Advance payment amount (RON): ")
    advance_date = input("Advance payment due date (DD/MM/YYYY): ")
    
    final_payment = input("Final payment amount (RON): ")
    final_date = input("Final payment due date (DD/MM/YYYY): ")
    
    state.contract_details.additional_info.update({
        "advance": advance,
        "advance_date": advance_date,
        "final_payment": final_payment,
        "final_date": final_date
    })

async def collect_object_details(state: AgentState) -> None:
    """
    Collect object details for buy-sell contracts.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if state.contract_details.contract_type != "buy-sell":
        return

    print("\nPlease enter contract object details:")
    print("Describe the object of sale (e.g., apartment, car, land):")
    
    object_description = input("Detailed description: ")
    
    state.contract_details.object_description = object_description
    state.contract_details.additional_info["object_description"] = object_description
>>>>>>> Stashed changes

async def agent_workflow() -> None:
    """
    Main agent workflow for processing documents and constructing a contract.
    """
    try:
        templates = load_templates(TEMPLATES_FOLDER)
        template_manager = TemplateManager(templates)
        documents = await process_documents()
        print("Documents processed.")
        state = AgentState()
        
        await process_pii_extraction(state, documents)
        await determine_contract_type(state, templates)
        await identify_contract_parties(state)
<<<<<<< Updated upstream
        
        # Stage 4: Construct the contract
        await construct_final_contract(state, template_manager)
=======
        await collect_object_details(state)
        await collect_payment_details(state)
        filepath = await construct_final_contract(state, template_manager)
>>>>>>> Stashed changes
        
        if state.contract:
<<<<<<< Updated upstream
            print("\nFinal Contract:")
            print(f"Parties: {', '.join([f'{', '.join(party.roles)}: {party.name}' for party in state.contract.parties])}")
            print(f"Address: {state.contract.address}")
            print(f"Terms: {state.contract.terms}")
=======
            print("\nFinal contract:")
            print("Contract has been generated and saved successfully.")
            print(f"You can find the complete contract in the file: {filepath}")
>>>>>>> Stashed changes
        else:
            print("No contract was created.")
    except asyncio.CancelledError:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logging.error(f"Error in agent_workflow: {str(e)}", exc_info=True)
    finally:
<<<<<<< Updated upstream
        print("\nContract automation process completed.")
=======
        print("\nContract automation process has been completed.")
>>>>>>> Stashed changes
        input("Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(agent_workflow())
