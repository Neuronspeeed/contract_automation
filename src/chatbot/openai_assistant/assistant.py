from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Any
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()
API_KEY = os.getenv('OPENAI_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting constants
ONE_MINUTE = 60
MAX_CALLS_PER_MINUTE = 50

def rate_limit(func: Callable) -> Callable:
    """Custom rate limiter decorator."""
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        self = args[0]
        current_time = datetime.now()
        if (current_time - self.last_request_time).seconds < ONE_MINUTE:
            if self.request_count >= MAX_CALLS_PER_MINUTE:
                wait_time = ONE_MINUTE - (current_time - self.last_request_time).seconds
                await asyncio.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = current_time
        return await func(*args, **kwargs)
    return wrapper

class ContractAssistant:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.thread = self.create_thread()
        self.assistant = self.create_assistant()
        self.request_count = 0
        self.last_request_time = datetime.now()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((TimeoutError, ConnectionError))
    )
    def create_thread(self):
        """Create a new thread with retry logic."""
        try:
            return self.client.beta.threads.create()
        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def create_assistant(self):
        """Create an assistant with retry logic."""
        try:
            return self.client.beta.assistants.create(
                name="Contract Assistant",
                instructions="""
                Ești un asistent specializat în colectarea informațiilor despre contracte.
                1. Determina tipul de contract:
                    - airbnb
                    - vanzare-cumparare
                    - consultanta IT
                2. Colectează cărțile de identitate și numerele de telefon
                3. Fii concis și direct în răspunsurile tale
                """,
                model="gpt-4o-mini",
            )
        except Exception as e:
            logger.error(f"Failed to create assistant: {e}")
            raise

    @rate_limit
    async def process_message(self, message: str) -> str:
        """Process user message with rate limiting and retry logic."""
        try:
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )

            # Create run with timeout
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )

            # Wait for completion with timeout
            timeout = 30  
            start_time = datetime.now()
            
            while run.status not in ["completed", "failed"]:
                if (datetime.now() - start_time).seconds > timeout:
                    raise TimeoutError("Request timed out")
                
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                
                if run.status == "failed":
                    raise Exception(f"Assistant failed: {run.last_error}")
                    
                await asyncio.sleep(0.5)

            # Get latest message
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order="desc",
                limit=1
            )

            # Update rate limiting counters
            self.request_count += 1
            self.last_request_time = datetime.now()

            return messages.data[0].content[0].text.value

        except TimeoutError as e:
            logger.error(f"Timeout error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.client.beta.assistants.delete(assistant_id=self.assistant.id)
            await self.client.beta.threads.delete(thread_id=self.thread.id)
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

class ContractInquiryEventHandler:
    def on_text_created(self, text: str) -> None:
        print(f"\nAssistant: {text}", end="", flush=True)

    def on_text_delta(self, delta: str) -> None:
        print(delta, end="", flush=True)

    def on_tool_call_created(self, tool_call: str) -> None:
        print(f"\nAssistant is using tool: {tool_call}\n", flush=True)

    def on_tool_call_delta(self, delta: dict) -> None:
        if delta.get('type') == 'text_analyzer':
            print(delta.get('text_analyzer', {}).get('output', ''), flush=True)

class ContractState:
    def __init__(self):
        self.contract_type: Optional[str] = None
        self.parties: Dict[str, str] = {}
        self.validated: bool = False

