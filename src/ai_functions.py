import json
import os
from openai import AsyncOpenAI
from typing import List, Dict
from pydantic import ValidationError
from models import ContractParties, Contract, PIIData, AgentState, AgentAction, ContractDetails, ContractParty
from config import API_KEY, SYSTEM_PROMPT
import instructor
import logging
import traceback



# Initialize OpenAI client with Instructor
client = instructor.patch(AsyncOpenAI(api_key=API_KEY))

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
async def extract_pii(text: str) -> List[PIIData]:
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract personal identifiable information from the following text:\n\n{text}"}
        ],
        response_model=List[PIIData]
    )
    return response

async def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    pii_text = "\n".join([f"Name: {pii.name}, Address: {pii.address}" for pii in pii_data])
    
    user_prompt = f"""
    For a {contract_type} contract, assign roles to the following parties:

    {pii_text}

    Your task is to ask for the roles of the each person in the context of a {contract_type} contract.
    Consider the following guidelines:

    1. For a buy-sell contract:
       - Ask who the buyer and who is the seller.

    2. For an airbnb contract:
       - Ask who is the landlord (property owner) and who is the tenant (guest).

    3. For an IT contract:
       - Ask who is the IT consultant and who is the client.

    For each person, provide:
    1. Their name
    2. Their possible roles and let the human choose only from the roles mentioned above.

    """
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_model=ContractParties
    )
    
    confirmed_parties = []
    for party in response.parties:
        print(f"\nPossible roles for {party.name}:")
        for i, role in enumerate(party.roles, 1):
            print(f"{i}. {role}")
        
        while True:
            choice = input(f"Select a role for {party.name} (enter the number): ")
            try:
                choice = int(choice)
                if 1 <= choice <= len(party.roles):
                    selected_role = party.roles[choice - 1]
                    confirmed_parties.append(ContractParty(name=party.name, roles=[selected_role]))
                    break
                else:
                    print("Invalid choice. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    return ContractParties(parties=confirmed_parties)


async def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    parties_info = ", ".join([f"{party.name} ({party.role})" for party in parties.parties])
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine the contract details for a {contract_type} contract with the following parties:\n\n{parties_info}"}
        ],
        response_model=ContractDetails
    )
    return response

async def construct_contract(parties: ContractParties, address: str, template: str, details: ContractDetails) -> Contract:
    parties_info = ", ".join([f"{', '.join(party.roles)}: {party.name}" for party in parties.parties])
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"""Construct a {details.contract_type} contract using the following template and information:

Template:
{template}

Parties: {parties_info}
Address: {address}
Additional Details: {details.additional_info}

Instructions:
1. Use the provided template as a base for the contract.
2. Insert the parties' names directly into the contract without brackets.
3. Use the provided address for the 'Address' field in the contract.
4. Ensure all placeholders in the template are replaced with appropriate information.
5. If any information is missing, leave the corresponding field blank or use a placeholder like [To be determined].
"""}
        ],
        response_model=Contract
    )
    return response

async def agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction:
    state_summary = f"""
    Current state:
    - Verified PII data: {len(state.verified_pii_data)} entries
    - Contract type: {state.contract_details.contract_type if state.contract_details else 'Not determined'}
    - Parties identified: {', '.join([f"{', '.join(party.roles)}: {party.name}" for party in state.parties.parties]) if state.parties else 'No'}
    - Contract constructed: {'Yes' if state.contract else 'No'}
    Available templates: {', '.join(templates.keys())}
    """
    
    response = await client.chat.completions.create(
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



