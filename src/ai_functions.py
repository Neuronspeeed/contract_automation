import json
import os
from openai import OpenAI
from typing import List, Dict
from pydantic import ValidationError
from models import ContractParties, Contract, PIIData, AgentState, AgentAction, ContractDetails, ContractParty
from config import API_KEY, SYSTEM_PROMPT
import instructor
import logging
import traceback



# Initialize OpenAI client with Instructor
client = instructor.patch(OpenAI(api_key=API_KEY))


# Function calling
functions = [
    {
        "name": "extract_pii",
        "description": "Extract personal identifiable information from text",
        "parameters": PIIData.model_json_schema()
    },
    {
        "name": "identify_parties",
        "description": "Identify the parties and their roles based on extracted PII data",
        "parameters": ContractParties.model_json_schema()
    },
    {
        "name": "determine_contract_details",
        "description": "Determine the contract details based on the contract type",
        "parameters": ContractDetails.model_json_schema()
    },
    {
        "name": "construct_contract",
        "description": "Construct a contract between the parties using a template",
        "parameters": Contract.model_json_schema()
    },
    {
        "name": "agent_action",
        "description": "Determine the next action for the agent to take",
        "parameters": AgentAction.model_json_schema()
    }
]

# Refactored functions to use OpenAI function calling with error handling
def extract_pii(text: str) -> List[PIIData]:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract personal identifiable information from the following text:\n\n{text}"}
        ],
        response_model=List[PIIData]
    )
    return response

def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    pii_text = "\n".join([f"Name: {pii.name}, Address: {pii.address}" for pii in pii_data])
    
    user_prompt = f"""
    For a {contract_type} contract, suggest possible roles for the following parties based on their personal information:

    {pii_text}

    Your task is to provide a list of 3 to 4 possible roles for each person in the context of a {contract_type} contract. 
    Include general roles like "Buyer" or "Seller" as well as more specific roles that might be relevant to this type of contract.
    Ensure that the suggested roles are diverse and appropriate for the contract type.
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_model=ContractParties
    )
    
    confirmed_parties = []
    for party in response.parties:
        possible_roles = party.role.split(', ')
        print(f"\nPossible roles for {party.name}:")
        for i, role in enumerate(possible_roles, 1):
            print(f"{i}. {role}")
        
        while True:
            choice = input(f"Select a role for {party.name} (enter the number): ")
            try:
                choice = int(choice)
                if 1 <= choice <= len(possible_roles):
                    selected_role = possible_roles[choice - 1]
                    confirmed_parties.append(ContractParty(name=party.name, role=selected_role))
                    break
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    return ContractParties(parties=confirmed_parties)

def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    parties_info = ", ".join([f"{party.name} ({party.role})" for party in parties.parties])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine the contract details for a {contract_type} contract with the following parties:\n\n{parties_info}"}
        ],
        response_model=ContractDetails
    )
    return response

def construct_contract(parties: ContractParties, address: str, template: str, details: ContractDetails) -> Contract:
    parties_info = ", ".join([f"{party.role}: {party.name}" for party in parties.parties])
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Construct a {details.contract_type} contract using the following template and information:\n\nTemplate:\n{template}\n\nParties: {parties_info}\nAddress: {address}\nAdditional Details: {details.additional_info}"}
        ],
        response_model=Contract
    )
    return response

def agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction:
    state_summary = f"""
    Current state:
    - Verified PII data: {len(state.verified_pii_data)} entries
    - Contract type: {state.contract_details.contract_type if state.contract_details else 'Not determined'}
    - Parties identified: {', '.join([f"{party.role}: {party.name}" for party in state.parties.parties]) if state.parties else 'No'}
    - Contract constructed: {'Yes' if state.contract else 'No'}
    Available templates: {', '.join(templates.keys())}
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{state_summary}\nBased on the current state and available templates, determine the next action to take in the contract creation process. Provide a structured response with the action and a detailed reason for your choice."}
        ],
        response_model=AgentAction
    )
    
    response.action = response.action.lower()
    print(f"Agent decided to: {response.action}")
    print(f"Reason: {response.reason}")
    return response



