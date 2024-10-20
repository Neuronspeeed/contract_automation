import json
import os
from openai import AsyncOpenAI
from typing import List, Dict
from pydantic import ValidationError
from models import ContractParties, Contract, PIIData, AgentState, AgentAction, ContractDetails, ContractParty
from config import API_KEY, SYSTEM_PROMPT
import instructor
from instructor import OpenAISchema
import logging
import traceback



# Initialize OpenAI client with Instructor
client = instructor.patch(AsyncOpenAI(api_key=API_KEY))


# Extract personal identifiable information from text.
async def extract_pii(text: str) -> List[PIIData]:
    """Extract personal identifiable information from text."""
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=List[PIIData],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract personal identifiable information from the following text:\n\n{text}"}
        ]
    )

# Identify the parties and their roles based on extracted PII data and contract type.
async def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    """Identify the parties and their roles based on extracted PII data and contract type."""
    pii_text = "\n".join([f"Name: {pii.name}, Address: {pii.address}" for pii in pii_data])
    
    user_prompt = f"""
    For a {contract_type} contract, assign roles to the following parties:

    {pii_text}

    Your task is to determine the roles of each person in the context of a {contract_type} contract.
    Consider the following guidelines:

    1. For a buy-sell contract:
       - Identify the buyer and the seller.

    2. For an airbnb contract:
       - Identify the landlord (property owner) and the tenant (guest).

    3. For an IT contract:
       - Identify the IT consultant and the client.

    For each person, provide their name and assigned role.
    """
    
    # Get roles from the AI
    roles_response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_model=ContractParties
    )

    # Assuming roles_response is a structured response from the AI
    roles = []
    for party in roles_response.parties:
        print(f"Identified party: {party.name}, Suggested role: {', '.join(party.roles)}")
        # Allow user confirmation or modification of roles
        user_confirmation = input(f"Do you want to keep this role for {party.name}? (yes/no): ")
        if user_confirmation.lower() != 'yes':
            new_role = input(f"Please assign a new role for {party.name}: ")
            roles.append((party.name, new_role))
        else:
            roles.append((party.name, party.roles[0]))  # Keep the suggested role

    # Create ContractParties object
    parties = [ContractParty(name=name, roles=[role]) for name, role in roles]
    return ContractParties(parties=parties)

# Determine the contract details based on the contract type.
async def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    """Determine the contract details based on the contract type."""
    parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in parties.parties])
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine the contract details for a {contract_type} contract with the following parties:\n\n{parties_info}"}
        ],
        response_model=ContractDetails
    )

async def construct_contract(parties: ContractParties, address: str, template: str, details: ContractDetails) -> Contract:
    """Construct a contract between the parties using a template."""
    parties_info = ", ".join([f"{', '.join(party.roles)}: {party.name}" for party in parties.parties])
    user_prompt = f"""Construct a {details.contract_type} contract using the following template and information:

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
"""

    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_model=Contract
    )

# Determine the next action for the agent to take.
async def agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction:
    """Determine the next action for the agent to take."""
    state_summary = f"""
    Current state:
    - Verified PII data: {len(state.verified_pii_data)} entries
    - Contract type: {state.contract_details.contract_type if state.contract_details else 'Not determined'}
    - Parties identified: {', '.join([f"{', '.join(party.roles)}: {party.name}" for party in state.parties.parties]) if state.parties else 'No'}
    - Contract constructed: {'Yes' if state.contract else 'No'}
    Available templates: {', '.join(templates.keys())}
    """
    
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine the next action based on the current state:\n\n{state_summary}"}
        ],
        tools=[{"type": "function", "function": {"name": "agent_action", "parameters": AgentAction.model_json_schema()}}],
        tool_choice={"type": "function", "function": {"name": "agent_action"}},
        response_model=AgentAction
    )




async def determine_contract_type(pii_data: List[PIIData], available_templates: List[str]) -> str:
    """Determine the contract type based on PII data and available templates."""
    pii_text = "\n".join([f"Name: {pii.name}, Address: {pii.address}" for pii in pii_data])
    templates_text = ", ".join(available_templates)
    
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Ask the user to choose the the contract  type from the following available templates:\n\nAvailable Templates: {templates_text}"}
        ],
        response_model=str
    )



