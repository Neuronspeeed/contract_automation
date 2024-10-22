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
import instructor
from instructor import OpenAISchema, llm_validator
import logging
import traceback

# Initialize OpenAI client with Instructor
client = instructor.patch(AsyncOpenAI(api_key=API_KEY))

async def extract_pii(text: str) -> List[PIIData]:
    """Extrage informații personale identificabile din text."""
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=List[PIIData],
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{PII_EXTRACTION_PROMPT}\n\n{text}"}
        ]
    )

async def determine_contract_type(pii_data: List[PIIData], available_templates: List[str]) -> str:
    """Determină tipul contractului bazat pe șabloanele disponibile."""
    templates_text = "\n".join([f"{i+1}. {template}" for i, template in enumerate(available_templates)])
    while True:
        try:
            selection = input(f"Vă rugăm să selectați tipul de contract din următoarele șabloane disponibile:\n{templates_text}\nSelectați (1-{len(available_templates)}): ").strip()
            selected_index = int(selection) - 1
            if 0 <= selected_index < len(available_templates):
                contract_type = available_templates[selected_index]
                # Validează tipul contractului folosind validatorul central
                return ContractRoleValidator.validate_contract_type(contract_type)
            else:
                print("Alegere invalidă. Vă rugăm să selectați un număr valid.")
        except ValueError:
            print("Input invalid. Vă rugăm să introduceți un număr.")

async def identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties:
    """Identifică părțile și rolurile lor bazate pe datele PII extrase și tipul contractului."""
    parties = []
    available_roles = get_role_options(contract_type)
    available_roles_text = "\n".join([f"{i+1}. {role}" for i, role in enumerate(available_roles)])

    for pii in pii_data:
        while True:
            print(f"\nVă rugăm să atribuiți un rol pentru următoarea parte:")
            print(f"Nume: {pii.name}, Adresă: {pii.address}")
            try:
                role_selection = input(f"Roluri disponibile pentru contractul de tip {contract_type}:\n{available_roles_text}\nSelectați rolul pentru {pii.name} (1-{len(available_roles)}): ").strip()
                selected_index = int(role_selection) - 1
                if 0 <= selected_index < len(available_roles):
                    selected_role = available_roles[selected_index]
                    # Validează rolul folosind validatorul central
                    ContractRoleValidator.validate_role(selected_role)
                    parties.append(ContractParty(name=pii.name, roles=[selected_role]))
                    break
                else:
                    print("Alegere invalidă. Vă rugăm să selectați un număr valid.")
            except ValueError:
                print("Input invalid. Vă rugăm să introduceți un număr.")

    return ContractParties(parties=parties)

async def determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails:
    """Determină detaliile contractului bazate pe tipul contractului."""
    parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in parties.parties])
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determină detaliile contractului pentru un contract de tip {contract_type} cu următoarele părți:\n\n{parties_info}"}
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
    """Construiește un contract bazat pe informațiile date și șablon."""
    parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in parties.parties])
    role_reminder = "Amintiți-vă să folosiți exact rolurile furnizate (de ex., 'Proprietar' și 'Chiriaș' pentru contractele Airbnb, nu 'Gazdă' și 'Oaspete')."
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=Contract,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{CONTRACT_CONSTRUCTION_PROMPT}\n\nTip Contract: {contract_type}\nȘablon:\n{template}\nPărți: {parties_info}\nAdresă: {address}\nInformații Adiționale: {additional_info}\n\n{role_reminder}"}
        ]
    )

async def agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction:
    """Determină următoarea acțiune pentru agent."""
    state_summary = f"""
    Stare curentă:
    - Date PII verificate: {len(state.verified_pii_data)} intrări
    - Tip contract: {state.contract_details.contract_type if state.contract_details else 'Nedeterminat'}
    - Părți identificate: {', '.join([f"{', '.join(party.roles)}: {party.name}" for party in state.parties.parties]) if state.parties else 'Nu'}
    - Contract construit: {'Da' if state.contract else 'Nu'}
    Șabloane disponibile: {', '.join(templates.keys())}
    """
    
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Determină următoarea acțiune bazată pe starea curentă:\n\n{state_summary}"}
        ],
        tools=[{"type": "function", "function": {"name": "agent_action", "parameters": AgentAction.model_json_schema()}}],
        tool_choice={"type": "function", "function": {"name": "agent_action"}},
        response_model=AgentAction
    )
