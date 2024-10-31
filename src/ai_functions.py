import json
import os
from openai import AsyncOpenAI
from typing import List, Dict
from models import (
    ContractParties,
    Contract,
    PIIData,
    AgentState,
    AgentAction,
    ContractDetails,
    ContractParty,
)
from config import API_KEY, TEMPLATES_FOLDER
from prompts import PII_EXTRACTION_PROMPT, PARTY_IDENTIFICATION_PROMPT, CONTRACT_CONSTRUCTION_PROMPT, SYSTEM_PROMPT
from validators import ContractRoleValidator
from role_options import get_role_options
from openai_client import client




async def extract_pii(text: str) -> List[PIIData]:
    """Extract personally identifiable information from text."""
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=List[PIIData],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{PII_EXTRACTION_PROMPT}\n\n{text}"}
        ]
    )

async def determine_contract_type(pii_data: List[PIIData], available_templates: List[str]) -> str:
    """Determine contract type based on available templates."""
    templates_text = "\n".join([f"{i+1}. {template}" for i, template in enumerate(available_templates)])
    while True:
        try:
            selection = input(f"Please select a contract type from the following available templates:\n{templates_text}\nSelect (1-{len(available_templates)}): ").strip()
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(available_templates):
                contract_type = available_templates[selected_index]
                return ContractRoleValidator.validate_contract_type(contract_type)
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    """Identify parties and their roles based on extracted PII data and contract type."""
    parties = []
    available_roles = get_role_options(contract_type)
    available_roles_text = "\n".join([f"{i+1}. {role}" for i, role in enumerate(available_roles)])

    for pii in pii_data:
        while True:
            print(f"\nPlease assign a role for the following party:")
            print(f"Name: {pii.name}, Address: {pii.address}")
            try:
                role_selection = input(f"Available roles for contract type {contract_type}:\n{available_roles_text}\nSelect role for {pii.name} (1-{len(available_roles)}): ").strip()
                selected_index = int(role_selection) - 1
                if 0 <= selected_index < len(available_roles):
                    selected_role = available_roles[selected_index]
                    ContractRoleValidator.validate_role(selected_role)
                    parties.append(ContractParty(name=pii.name, roles=[selected_role]))
                    break
                else:
                    print("Invalid choice. Please select a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    return ContractParties(parties=parties)

async def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    """Determine contract details based on contract type."""
    parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in parties.parties])
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determine contract details for a contract of type {contract_type} with the following parties:\n\n{parties_info}"}
        ],
        response_model=ContractDetails
    )

async def construct_contract(
    contract_type: str,
    parties: ContractParties,
    address: str,
    additional_info: Dict[str, str],
    template: str
) -> Contract:
    """Construct a contract based on the provided information and template."""
    parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in parties.parties])
    object_description = additional_info.get('object_description', '[To be determined]')
    role_reminder = "Remember to use the exact roles provided (e.g., 'Owner' and 'Renter' for Airbnb contracts, not 'Landlord' and 'Tenant')."
    
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Contract,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{CONTRACT_CONSTRUCTION_PROMPT}\n\nContract Type: {contract_type}\nTemplate:\n{template}\nParties: {parties_info}\nAddress: {address}\nAdditional Information: {additional_info}\nObject Description: {object_description}\n\n{role_reminder}"}
        ]
    )

async def agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction:
    """Determine the next action for the agent."""
    state_summary = f"""
    Current State:
    - PII Data Verified: {len(state.verified_pii_data)} entries
    - Contract Type: {state.contract_details.contract_type if state.contract_details else 'Undetermined'}
    - Parties Identified: {', '.join([f"{', '.join(party.roles)}: {party.name}" for party in state.parties.parties]) if state.parties else 'None'}
    - Contract Constructed: {'Yes' if state.contract else 'No'}
    Available Templates: {', '.join(templates.keys())}
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
