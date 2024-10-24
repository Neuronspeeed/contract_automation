import instructor
from openai import AsyncOpenAI
from config import API_KEY

# Initialize OpenAI client with Instructor
client = instructor.patch(AsyncOpenAI(api_key=API_KEY))
