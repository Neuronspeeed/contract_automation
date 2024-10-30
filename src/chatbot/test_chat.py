import asyncio
import os
from dotenv import load_dotenv
from src.chatbot.assistant import ContractAssistant

async def test_chat():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: Please set OPENAI_API_KEY in .env file")
        return
        
    # Initialize assistant
    assistant = ContractAssistant(api_key)
    
    print("🤖 Contract Assistant Chat")
    print("Commands:")
    print("- Type 'workflow' to start the guided workflow")
    print("- Type any message to chat with the AI")
    print("- Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'quit':
            break
            
        if user_input.lower() == 'workflow':
            await assistant.process_workflow()
            continue
            
        response = await assistant.process_message(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    asyncio.run(test_chat()) 