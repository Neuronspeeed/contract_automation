import os
from openai import OpenAI
from typing import List, Dict
from pydantic import ValidationError
from models import ContractParties, Contract, PIIData, AgentState, AgentAction, ContractDetails
from config import API_KEY, SYSTEM_PROMPT
import instructor
import logging



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
        "description": "Identify the buyer and seller based on extracted PII data",
        "parameters": {
            "type": "object",
            "properties": {
                "buyer": {"type": "string", "description": "Name of the buyer"},
                "seller": {"type": "string", "description": "Name of the seller"}
            },
            "required": ["buyer", "seller"]
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
        "description": "Construct a contract between the buyer and seller using a template",
        "parameters": {
            "type": "object",
            "properties": {
                "buyer": {"type": "string", "description": "Name of the buyer"},
                "seller": {"type": "string", "description": "Name of the seller"},
                "address": {"type": "string", "description": "Address of the property"},
                "terms": {"type": "string", "description": "Terms of the contract"},
                "contract_type": {"type": "string", "description": "Type of contract"},
                "additional_info": {
                    "type": "object",
                    "description": "Additional information specific to the contract type",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["buyer", "seller", "address", "terms", "contract_type", "additional_info"]
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
def extract_pii(text: str) -> PIIData:
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract the name and address from the given text:\n\n{text}"}
            ],
            response_model=PIIData
        )
        return response
    except Exception as e:
        logging.error(f"Error in extract_pii: {str(e)}")
        raise

# Similarly refactor `identify_parties` and `construct_contract` functions
def identify_parties(pii_data: List[PIIData]) -> ContractParties:
    pii_text = "\n".join([f"Name: {pii.name}, Address: {pii.address}" for pii in pii_data])
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Identify the buyer and seller from the given information:\n\n{pii_text}"}
        ],
        response_model=ContractParties
    )

def construct_contract(parties: ContractParties, address: str, template: str) -> Contract:
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a contract using the following template:\n\n{template}\n\nBuyer: {parties.buyer}, Seller: {parties.seller}, Address: {address}"}
        ],
        response_model=Contract
    )

def agent_action(state: AgentState) -> AgentAction:
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Current state: {state.dict()}\nWhat action should be taken next? Choose from: extract_pii, identify_parties, determine_contract_type, construct_contract, finish"}
        ],
        response_model=AgentAction
    )

def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine the contract details for a {contract_type} contract between {parties.buyer} and {parties.seller}."}
        ],
        response_model=ContractDetails
    )
