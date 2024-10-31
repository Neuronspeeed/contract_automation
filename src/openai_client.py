from openai import AsyncOpenAI
import instructor
from config import API_KEY

# Initialize OpenAI client with Instructor
client = instructor.from_openai(
    AsyncOpenAI(api_key=API_KEY), 
    mode=instructor.Mode.TOOLS_STRICT  
)
