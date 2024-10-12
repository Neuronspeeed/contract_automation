from typing import List
from openai import OpenAI
import instructor
from src.templates.config import API_KEY, SYSTEM_PROMPT
from src.models import PIIData, ContractParties, Contract

# Initialize OpenAI client with Instructor
client = instructor.patch(OpenAI(api_key=API_KEY))

def extract_pii(text: str) -> PIIData:
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract the name and address from the given text:\n\n{text}"}
        ],
        response_model=PIIData
    )

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

def construct_contract(parties: ContractParties, address: str) -> Contract:
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a contract between the buyer and seller. Buyer: {parties.buyer}, Seller: {parties.seller}, Address: {address}"}
        ],
        response_model=Contract
    )
