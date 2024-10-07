from .state import ContractState, PiiDataModel, ContractPartiesModel
from .utils import get_documents, extract_text
from langchain_core.messages import AIMessage
from openai import OpenAI
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

system_prompt = (
    "You are an AI legal assistant specializing in contract creation and personal information extraction. "
    "Your role is to ensure all responses are formatted clearly, focusing on accuracy, privacy, and legality. "
    "Always ask clarifying questions if any information is incomplete or unclear. Respond concisely and use formal language appropriate for legal contexts."
    "Include all relevant details explicitly and structure output for easy readability."
)

async def extract_pii_and_address(state: dict | ContractState) -> ContractState:
    if isinstance(state, dict):
        state = ContractState(**state)

    documents = get_documents()
    logger.debug(f"Documents found: {documents}")

    if not documents:
        state.messages.append(AIMessage(content="No documents found in the data folder."))
        return state

    for doc in documents:
        try:
            extracted_text = await extract_text(doc)
            logger.debug(f"Extracted text from {doc}: {extracted_text[:100]}...")
            
            # Update the extracted_texts field
            state.extracted_texts[doc] = extracted_text
            
            # Update the extracted_text field with the latest extracted text
            state.extracted_text = extracted_text

            if not extracted_text:
                state.messages.append(AIMessage(content=f"Unable to extract text from {doc}"))
                continue

            pii_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract the full name and address from this text:\n\n{extracted_text}"}
                ],
                functions=[{
                    "name": "extract_pii_data",
                    "description": "Extracts the person's full name and address from the provided text.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Full name of the person."},
                            "address": {"type": "string", "description": "Residential address of the person."}
                        },
                        "required": ["name", "address"]
                    }
                }],
                function_call={"name": "extract_pii_data"}
            )

            pii_data = json.loads(pii_response.choices[0].message.function_call.arguments)
            
            pii_data_model = PiiDataModel(**pii_data)
            state.pii_data = pii_data_model.dict()
            state.address = pii_data_model.address
            state.messages.append(AIMessage(content=f"Extracted PII from {doc}: {pii_data}"))
            return state

        except Exception as e:
            state.messages.append(AIMessage(content=f"Unexpected error processing {doc}: {str(e)}"))
            logger.error(f"Error processing document {doc}: {str(e)}")

    if not state.pii_data:
        state.messages.append(AIMessage(content="Failed to extract PII from any document."))
    
    return state

def missing_information(state: ContractState) -> ContractState:
    state.messages.append(AIMessage(content="Please provide the missing information regarding PII or address."))
    return state

def human_verification(state: ContractState) -> ContractState:
    verification_prompt = f"Is this information correct?\nName: {state.pii_data['name']}, Address: {state.address}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": verification_prompt}
        ],
        max_tokens=50,
        temperature=0.7
    )
    state.messages.append(AIMessage(content=response.choices[0].message.content.strip()))
    return state

def identify_buyer_and_seller(state: ContractState) -> ContractState:
    functions = [
        {
            "name": "identify_parties",
            "description": "Identifies the buyer and seller from the given text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer": {"type": "string", "description": "Name of the buyer."},
                    "seller": {"type": "string", "description": "Name of the seller."}
                },
                "required": ["buyer", "seller"]
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Identify the buyer and seller from the context."}
        ],
        functions=functions,
        function_call="auto"
    )
    parties = json.loads(response.choices[0].message.function_call.arguments)
    parties_model = ContractPartiesModel(**parties)
    state.buyer = parties_model.buyer
    state.seller = parties_model.seller
    return state

def construct_contract(state: ContractState) -> ContractState:
    functions = [
        {
            "name": "generate_contract",
            "description": "Generates a contract between buyer and seller for the given address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "buyer": {"type": "string", "description": "Name of the buyer."},
                    "seller": {"type": "string", "description": "Name of the seller."},
                    "address": {"type": "string", "description": "Address where the contract is applicable."}
                },
                "required": ["buyer", "seller", "address"]
            }
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Create a contract between buyer and seller using the provided information."}
        ],
        functions=functions,
        function_call="auto"
    )

    try:
        contract_data = json.loads(response.choices[0].message.function_call.arguments)
        
        parties_model = ContractPartiesModel(**contract_data)
        state.buyer = parties_model.buyer
        state.seller = parties_model.seller
        state.address = contract_data['address']
        
        state.contract = (
            f"This contract is made between {state.buyer} (Buyer) and {state.seller} (Seller), "
            f"with the following terms to apply at {state.address}."
        )

        state.messages.append(AIMessage(content=f"Contract created: {state.contract}"))

    except json.JSONDecodeError:
        state.messages.append(AIMessage(content="Error decoding JSON response while constructing the contract."))
    except ValueError as e:
        state.messages.append(AIMessage(content=f"Validation error while constructing the contract: {str(e)}"))
    except Exception as e:
        state.messages.append(AIMessage(content=f"Unexpected error while constructing the contract: {str(e)}"))

    return state