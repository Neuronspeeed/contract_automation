import asyncio
import os
from dotenv import load_dotenv
from assistant import ContractAssistant

async def main():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: Please set OPENAI_API_KEY in .env file")
        return
        
    assistant = ContractAssistant(api_key)
    print("🤖 Hello! How can I help you today?")
    
    while True:
        msg = input("\nYou: ")
        if msg.lower() == 'quit':
            break
        if msg.lower() == 'workflow':
            await assistant.process_workflow()
            continue
        response = await assistant.process_message(msg)
        print(f"Assistant: {response}")

if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(main()) 