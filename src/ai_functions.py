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
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name of the person"},
                "address": {"type": "string", "description": "Residential address of the person"}
            },
            "required": ["name", "address"]
        }
    },
    {
        "name": "identify_parties",
        "description": "Identify the parties and their roles based on extracted PII data",
        "parameters": {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the party"},
                            "role": {"type": "string", "description": "Role of the party in the contract"}
                        },
                        "required": ["name", "role"]
                    }
                }
            },
            "required": ["parties"]
        }
    },
    {
        "name": "determine_contract_details",
        "description": "Determine the contract details based on the contract type",
        "parameters": {
            "type": "object",
            "properties": {
                "contract_type": {"type": "string", "description": "Type of contract (e.g., airbnb, buy-sell, it-consulting)"},
                "additional_info": {
                    "type": "object",
                    "description": "Additional information specific to the contract type",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["contract_type", "additional_info"]
        }
    },
    {
        "name": "construct_contract",
        "description": "Construct a contract between the parties using a template",
        "parameters": {
            "type": "object",
            "properties": {
                "parties": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Name of the party"},
                            "role": {"type": "string", "description": "Role of the party in the contract"}
                        },
                        "required": ["name", "role"]
                    }
                },
                "address": {"type": "string", "description": "Address of the property"},
                "terms": {"type": "string", "description": "Terms of the contract"},
                "contract_type": {"type": "string", "description": "Type of contract"},
                "additional_info": {
                    "type": "object",
                    "description": "Additional information specific to the contract type",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["parties", "address", "terms", "contract_type", "additional_info"]
        }
    },
    {
        "name": "agent_action",
        "description": "Determine the next action for the agent to take",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "description": "Action to be performed by the agent"},
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the action",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["action", "parameters"]
        }
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
    For a {contract_type} contract, suggest roles for the following parties based on their personal information:

    {pii_text}

    Your task is to suggest appropriate roles for each person in the context of a {contract_type} contract. 
    The human will then confirm or modify these suggestions.
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
        print(f"\nSuggested role for {party.name}: {party.role}")
        confirmation = input(f"Is this role correct for {party.name}? (yes/no): ").lower()
        if confirmation != 'yes':
            new_role = input(f"Please enter the correct role for {party.name}: ")
            confirmed_parties.append(ContractParty(name=party.name, role=new_role))
        else:
            confirmed_parties.append(party)
    
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
    - Contract type determined: {'Yes' if state.contract_details and state.contract_details.contract_type else 'No'}
    - Parties identified: {'Yes' if state.parties and state.parties.parties else 'No'}
    - Contract constructed: {'Yes' if state.contract else 'No'}
    Available templates: {', '.join(templates.keys())}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{state_summary}\nBased on the current state and available templates, determine the next action to take in the contract creation process. If the contract type is not determined, suggest asking the human for the contract type. Provide a detailed explanation for your choice."}
        ],
        response_model=AgentAction
    )
    
    # Ensure the action is lowercase to match the expected format in agent_workflow
    response.action = response.action.lower()
    
    print(f"Agent decided to: {response.action}")
    print(f"Reason: {response.parameters.get('reason', 'No reason provided')}")
    return response




