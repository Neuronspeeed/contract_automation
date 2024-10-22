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

print(f"Directorul de lucru curent: {os.getcwd()}")
print(f"Calea folderului de șabloane: {os.path.abspath(TEMPLATES_FOLDER)}")

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
            print("Vă rugăm să verificați următoarele informații:")
            print(f"Nume: {pii.name}")
            print(f"Adresă: {pii.address}")
            is_correct = input("Aceste informații sunt corecte? (da/nu): ").lower()
            if is_correct == 'da':
                verified_pii_data.append(pii)
            else:
                name = input("Vă rugăm să furnizați numele corect: ")
                address = input("Vă rugăm să furnizați adresa corectă: ")
                verified_pii_data.append(PIIData(name=name, address=address))
    
    state.verified_pii_data = verified_pii_data
    print(f"Date PII verificate: {len(state.verified_pii_data)} intrări")


# Determine the contract type based on PII data and available templates.
async def determine_contract_type(state: AgentState, templates: Dict[str, Dict]) -> None:
    """
    Allow the user to choose the contract type based on available templates.
    
    Args:
        state (AgentState): The current state of the agent.
        templates (Dict[str, Dict]): The loaded contract templates.
    """
    available_templates = list(templates.keys())
    print("\nTipuri de contract disponibile:")
    for i, template in enumerate(available_templates, 1):
        print(f"{i}. {template.split('.')[0]}")
    
    while True:
        choice = input(f"\nVă rugăm să alegeți un tip de contract (1-{len(available_templates)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(available_templates):
            selected_template = available_templates[int(choice) - 1]
            contract_type = selected_template.split('.')[0]
            state.contract_details = ContractDetails(contract_type=contract_type, additional_info={})
            print(f"\nTip de contract selectat: {state.contract_details.contract_type}")
            break
        else:
            print(f"Alegere invalidă. Vă rugăm să introduceți un număr între 1 și {len(available_templates)}.")

# Identify the parties involved in the contract using AI.
async def identify_contract_parties(state: AgentState) -> None:
    """
    Identify the parties involved in the contract using AI.
    
    Args:
        state (AgentState): The current state of the agent.
    """
    if not state.contract_details or not state.contract_details.contract_type:
        print("Tipul contractului nu a fost încă determinat. Vă rugăm să determinați mai întâi tipul contractului.")
        return
    
    state.parties = await ai_functions.identify_parties(state.verified_pii_data, state.contract_details.contract_type)
    print("\nPărți identificate:")
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
        print("Detaliile contractului sau părțile nu au fost încă determinate. Vă rugăm să completați mai întâi acești pași.")
        return
    
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
        print("Contract construit.")
    except Exception as e:
        print(f"Eroare la construirea contractului: {str(e)}")

# Main agent workflow for processing documents and constructing a contract.
async def agent_workflow() -> None:
    """
    Main agent workflow for processing documents and constructing a contract.
    """
    try:
        templates = load_templates(TEMPLATES_FOLDER)
        template_manager = TemplateManager(templates)
        documents = await process_documents()
        print("Documente procesate.")
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
            print("\nContract final:")
            print(f"Părți: {', '.join([f'{', '.join(party.roles)}: {party.name}' for party in state.contract.parties])}")
            print(f"Adresă: {state.contract.address}")
            print(f"Termeni: {state.contract.terms}")
        else:
            print("Nu a fost creat niciun contract.")
    except asyncio.CancelledError:
        print("\nOperațiune anulată de utilizator.")
    except Exception as e:
        print(f"A apărut o eroare: {str(e)}")
        logging.error(f"Error in agent_workflow: {str(e)}", exc_info=True)
    finally:
        print("\nProcesul de automatizare a contractului a fost finalizat.")
        input("Apăsați Enter pentru a ieși...")

if __name__ == "__main__":
    asyncio.run(agent_workflow())
