import os
import asyncio
import aiofiles
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.messages import AIMessage, HumanMessage
from models import ContractState, ContractPartiesModel
from utils import get_documents
from config import client, system_prompt, reader
from copy import deepcopy
from langgraph.graph import END

async def extract_text(file_path: str) -> str:
    if file_path.lower().endswith('.pdf'):
        try:
            loader = PyPDFLoader(file_path)
            pages = await asyncio.to_thread(loader.load)
            return "\n".join(page.page_content for page in pages)
        except ImportError:
            return "Error: PyPDFLoader not available. Please install langchain."
    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            def process_image():
                results = reader.readtext(file_path)
                return ' '.join([result[1] for result in results])
            return await asyncio.to_thread(process_image)
        except Exception as e:
            return f"Error processing image: {str(e)}"
    else:
        try:
            async with aiofiles.open(file_path, mode='r') as f:
                return await f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

async def process_documents(state: ContractState) -> ContractState:
    documents = get_documents()
    results = {}
    for doc in documents:
        try:
            text = await extract_text(doc)
            results[os.path.basename(doc)] = text
        except Exception as e:
            results[os.path.basename(doc)] = f"Error processing file: {str(e)}"
    state.extracted_texts = results
    return state

async def extract_pii_and_address(state: ContractState) -> ContractState:
    extracted_texts = state.extracted_texts
    print(f"Documents found: {len(extracted_texts)}")

    if not extracted_texts:
        print("No documents found or processed in the data folder.")
        return state

    new_state = deepcopy(state)
    new_state.pii_data = []

    for doc, extracted_text in extracted_texts.items():
        print(f"Processing document: {doc}")
        try:
            if not extracted_text or extracted_text.startswith("Error"):
                print(f"Unable to process text from {doc}: {extracted_text}")
                continue

            pii_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": extracted_text}
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

            function_call = pii_response.choices[0].message.function_call
            if function_call and function_call.arguments:
                pii_data = json.loads(function_call.arguments)
                new_state.pii_data.append({"document": doc, "data": pii_data})
                print(f"Extracted PII from {doc}: {pii_data}")
            else:
                print(f"No PII data extracted from {doc}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response for {doc}: {str(e)}")
        except Exception as e:
            print(f"Unexpected error processing {doc}: {str(e)}")

    if not new_state.pii_data:
        print("Failed to extract PII from any document.")

    return new_state

async def human_verification(state: ContractState) -> ContractState:
    if isinstance(state.pii_data, list) and len(state.pii_data) > 0:
        name = state.pii_data[0].get("data", {}).get("name", "")
        address = state.pii_data[0].get("data", {}).get("address", "")

        if not name or not address:
            state.messages.append(AIMessage(content="No valid name or address found for verification."))
            return state

        verification_prompt = f"Generate a simple yes/no question to verify this information: Name: {name}, Address: {address}"
        
        question_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": verification_prompt}
            ],
            max_tokens=50
        )
        
        verification_question = question_response.choices[0].message.content.strip()
        
        state.messages.append(AIMessage(content=f"Human verification required. {verification_question}"))
        
        simulated_human_response = "Yes, the information is correct."
        state.messages.append(HumanMessage(content=simulated_human_response))
        
        evaluation_prompt = f"Question: {verification_question}\nResponse: {simulated_human_response}\n\nDoes this response indicate that the information is correct? Respond with 'VERIFIED' if it does, or 'NOT VERIFIED' if it doesn't."
        
        evaluation_response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": evaluation_prompt}
            ],
            max_tokens=10
        )
        
        evaluation = evaluation_response.choices[0].message.content.strip()
        
        if evaluation == "VERIFIED":
            state.messages.append(AIMessage(content="Human verification successful. Proceeding with the process."))
        else:
            state.messages.append(AIMessage(content="Human verification failed. Please check the information and try again."))
            return END
    else:
        state.messages.append(AIMessage(content="No PII data found for verification."))

    return state

async def missing_information(state: ContractState) -> ContractState:
    new_state = deepcopy(state)
    new_state.messages.append(AIMessage(content="Please provide the missing information regarding PII or address."))
    return new_state

async def identify_buyer_and_seller(state: ContractState) -> ContractState:
    new_state = deepcopy(state)
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

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Identify the buyer and seller from the context."}
        ],
        functions=functions,
        function_call="auto"
    )
    parties = json.loads(response.choices[0].function_call.arguments)
    parties_model = ContractPartiesModel(**parties)
    new_state.buyer = parties_model.buyer
    new_state.seller = parties_model.seller
    return new_state

async def construct_contract(state: ContractState) -> ContractState:
    new_state = deepcopy(state)
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

    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Create a contract between buyer and seller using the provided information."}
        ],
        functions=functions,
        function_call="auto"
    )

    try:
        contract_data = json.loads(response.choices[0].function_call.arguments)
        parties_model = ContractPartiesModel(**contract_data)
        new_state.buyer = parties_model.buyer
        new_state.seller = parties_model.seller
        new_state.address = contract_data['address']
        new_state.contract = (
            f"This contract is made between {new_state.buyer} (Buyer) and {new_state.seller} (Seller), "
            f"with the following terms to apply at {new_state.address}."
        )
        new_state.messages.append(AIMessage(content=f"Contract created: {new_state.contract}"))
    except json.JSONDecodeError:
        new_state.messages.append(AIMessage(content="Error decoding JSON response while constructing the contract."))
    except ValueError as e:
        new_state.messages.append(AIMessage(content=f"Validation error while constructing the contract: {str(e)}"))
    except Exception as e:
        new_state.messages.append(AIMessage(content=f"Unexpected error while constructing the contract: {str(e)}"))

    return new_state