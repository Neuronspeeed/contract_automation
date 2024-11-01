import os
from typing import Annotated
from dotenv import load_dotenv
from openai import OpenAI




client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


async def main():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: Please set OPENAI_API_KEY in .env file")
        return
    

async def main():
    load_dotenv()
    api_key = os.getenv('TAVILY_API_KEY')

    if not api_key:
        print("Error: Please set TAVILY_API_KEY in .env file")
        return
    

class TavilyClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_search_context(self, query, search_depth="advanced"):
        # Placeholder for Tavily API request (replace with actual request implementation)
        return f"Mocked response for query: {query}"

# Initialize Tavily client
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Search tool using Tavily API for legal queries
def legal_search_tool(query: Annotated[str, "Legal search query"]):
    return tavily.get_search_context(query=query, search_depth="advanced")

# Function for the ReAct prompt template
def generate_react_prompt(input_question):
    return f"""
Answer the following legal question as best you can using available tools.

Use the following format:

Question: the input legal question
Thought: think about the steps to find the answer
Action: decide on the action to take (e.g., search)
Action Input: the input for the action (e.g., the search query)
Observation: result of the action
... (repeat this process if needed)
Thought: I now know the final answer
Final Answer: the final legal answer

Begin!
Question: {input_question}
"""

# GDPR Compliance Document
GDPR_COMPLIANCE_DOCUMENT = """
1. Data transfers to non-EU countries must follow standard contractual clauses (SCCs) or have explicit legal justifications.
   Transfers to US-based platforms should be paused until SCCs are updated in line with Schrems II and related rulings.
   
2. Automated decision-making (ADM) systems, including credit scoring, AI-based recruiting, and targeted advertising, must be evaluated for GDPR Article 22 compliance.
   Explicit consent must be obtained, and data subjects must be given an opt-out option in high-risk cases.

3. Data processing activities must align with GDPR Article 44, and vulnerability audits should be conducted twice a year to avoid breach-related liability.

4. Contracts with third-party processors, especially those in ad tech, should be reviewed every six months. Ad tech contracts must ensure restrictions on data usage for targeted advertising, following Meta rulings.

5. If non-compliance is detected, data transfers must be halted immediately until a thorough review is completed, especially transfers to high-risk regions like the US.

6. Protocols should be set up to handle claims for non-material damages, including emotional harm, based on recent interpretations of GDPR rulings.
"""

# Function for Insights prompt template
def generate_insights_prompt(legal_info):
    return f"""
Based on the following legal information and the GDPR compliance document, analyze the implications and suggest specific actions.

Input:
{legal_info}

GDPR Compliance Document:
{GDPR_COMPLIANCE_DOCUMENT}

Your task is to:
- Analyze the case rulings in light of the updated GDPR compliance document.
- Suggest any tailored actions the company must take, such as updating contracts, halting transfers, auditing ADM systems, etc.
"""

# Update the ask_openai function to use the new API pattern
def ask_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using latest model
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.5
    )
    return response.choices[0].message.content

# Example Workflow
if __name__ == "__main__":
    # Step 1: Legal Research with Tavily
    question = "What are the recent court rulings on GDPR and data privacy in the EU?"
    react_prompt = generate_react_prompt(question)
    react_response = ask_openai(react_prompt)
    print("Legal Research Response:")
    print(react_response)

    # Assuming the response from the legal research step
    legal_info = "The rulings retrieved by the Legal Research Agent..."
    
    # Step 2: Insights based on GDPR compliance
    insights_prompt = generate_insights_prompt(legal_info)
    insights_response = ask_openai(insights_prompt)
    print("\nLegal Insights Response:")
    print(insights_response)
