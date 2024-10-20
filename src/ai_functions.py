import json
import os
from openai import AsyncOpenAI
from typing import List, Dict
from pydantic import ValidationError
from models import ContractParties, Contract, PIIData, AgentState, AgentAction, ContractDetails, ContractParty
from config import API_KEY, SYSTEM_PROMPT, PII_EXTRACTION_PROMPT, PARTY_IDENTIFICATION_PROMPT, CONTRACT_CONSTRUCTION_PROMPT
import instructor
from instructor import OpenAISchema
import logging
import traceback

# Initialize OpenAI client with Instructor
client = instructor.patch(AsyncOpenAI(api_key=API_KEY))

async def extract_pii(text: str) -> List[PIIData]:
    """Extract personal identifiable information from text."""
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=List[PIIData],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{PII_EXTRACTION_PROMPT}\n\n{text}"}
        ]
    )

async def determine_contract_type(pii_data: List[PIIData], available_templates: List[str]) -> str:
    """Determine the contract type based on available templates."""
    templates_text = "\n".join([f"{i+1}. {template}" for i, template in enumerate(available_templates)])
    while True:
        try:
            selection = input(f"Please select the type of contract from the following available templates:\n{templates_text}\nSelect (1-{len(available_templates)}): ").strip()
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(available_templates):
                return available_templates[selected_index]
            else:
                print("Invalid choice. Please select a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

async def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    """Identify the parties and their roles based on extracted PII data and contract type."""
    parties = []
    role_options = {
        "airbnb": ["Landlord", "Tenant"],
        "buy-sell": ["Buyer", "Seller"],
        "it": ["Consultant", "Client"]
    }
    
    available_roles = role_options.get(contract_type.lower(), [])
    available_roles_text = "\n".join([f"{i+1}. {role}" for i, role in enumerate(available_roles)])
    
    for pii in pii_data:
        while True:
            print(f"\nPlease assign a role for the following party:")
            print(f"Name: {pii.name}, Address: {pii.address}")
            try:
                role_selection = input(f"Available Roles for {contract_type} contract:\n{available_roles_text}\nSelect the role for {pii.name} (1-{len(available_roles)}): ").strip()
                selected_index = int(role_selection) - 1
                if 0 <= selected_index < len(available_roles):
                    parties.append(ContractParty(name=pii.name, roles=[available_roles[selected_index]]))
                    break
                else:
                    print("Invalid choice. Please select a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    return ContractParties(parties=parties)

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
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": CONTRACT_CONSTRUCTION_PROMPT.format(
                contract_type=details.contract_type,
                template=template,
                parties_info=parties_info,
                address=address,
                additional_info=details.additional_info
            )}
        ],
        response_model=Contract
    )

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
