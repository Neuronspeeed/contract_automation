import asyncio
from models import ContractState
from graph import create_graph

async def run_graph():
    app = create_graph()
    initial_state = ContractState(messages=[], extracted_texts={})
    
    try:
        result_state = await app.ainvoke(initial_state)
        
        print("\nFinal Messages:")
        for message in result_state.messages:
            print(message.content)
        
        if result_state.pii_data:
            print("\nExtracted PII Data:")
            for item in result_state.pii_data:
                print(f"\nDocument: {item['document']}")
                print(json.dumps(item['data'], indent=2))

        if result_state.extracted_texts:
            print("\nExtracted Texts:")
            for filename, text in result_state.extracted_texts.items():
                print(f"File: {filename}")
                print(f"Text Extract: {text[:100]}...")  
    except Exception as e:
        print(f"Error during graph execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_graph())