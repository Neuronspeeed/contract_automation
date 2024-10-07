import asyncio
from contract_automation.nodes import extract_pii_and_address
from contract_automation.state import ContractState

async def test_extract_text():
    state = ContractState()  # Correctly initialize ContractState
    result = await extract_pii_and_address(state)
    print("Extracted texts:")
    for doc, text in result.extracted_texts.items():
        print(f"{doc}: {text[:100]}...")  # Print first 100 characters of each extracted text

if __name__ == "__main__":
    asyncio.run(test_extract_text())
