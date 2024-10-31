from openai import AsyncOpenAI
import instructor
import os
from dotenv import load_dotenv

def create_client(api_key: str):
    """Create and return an instructor-patched OpenAI client."""
    return instructor.from_openai(
        AsyncOpenAI(api_key=api_key),
        mode=instructor.Mode.TOOLS_STRICT
    )