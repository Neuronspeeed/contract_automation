import asyncio
import nest_asyncio
from src.document_processing import process_documents
from src.ai_functions import extract_pii, identify_parties, construct_contract
from src.utils import verify_information
from src.models import PIIData

# Apply nest_asyncio
nest_asyncio.apply()

async def agent_workflow():
    # Process documents
    documents = await process_documents()
    print("Documents processed.")

    # Extract PII and address, verify with human input
    verified_pii_data = []
    for doc, text in documents.items():
        print(f"Processing document: {doc}")
        while True:
            pii = extract_pii(text)
            if verify_information(pii):
                verified_pii_data.append(pii)
                break
            else:
                print("Please provide the correct information:")
                name = input("Name: ")
                address = input("Address: ")
                pii = PIIData(name=name, address=address)
                if verify_information(pii):
                    verified_pii_data.append(pii)
                    break

    # Identify buyer and seller
    parties = identify_parties(verified_pii_data)
    print(f"\nParties identified - Buyer: {parties.buyer}, Seller: {parties.seller}")

    # Construct contract
    contract = construct_contract(parties, verified_pii_data[0].address)
    print("\nContract constructed:")
    print(f"Buyer: {contract.buyer}")
    print(f"Seller: {contract.seller}")
    print(f"Address: {contract.address}")
    print(f"Terms: {contract.terms}")

if __name__ == "__main__":
    asyncio.run(agent_workflow())
