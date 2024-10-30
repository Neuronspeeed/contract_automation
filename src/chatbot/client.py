from typing import Optional
from assistant2 import ContractAssistant
import asyncio
import os
from dotenv import load_dotenv

async def chat_with_assistant() -> None:
    """Interactive chat loop with the Contract Assistant."""
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
        
    assistant = None
    try:
        assistant = ContractAssistant(api_key)
        print("Chat started (type 'quit' to exit)")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit']:
                break
                
            response = await assistant.process_message(user_input)
            print(f"\nAssistant: {response}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if assistant:
            await assistant.cleanup()

if __name__ == "__main__":
    asyncio.run(chat_with_assistant())