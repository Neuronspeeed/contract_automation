PII_EXTRACTION_PROMPT = """
Extract full name and complete address from documents, including building and apartment. Ignore all identification numbers, codes, and other information.

Examples:
1. Input: "ID CARD, Last Name SMITH, First Name JOHN, SSN 123456789, Series XX no 123456"
   Output: {"name": "SMITH JOHN", "address": "Not provided"}

2. Input: "ID CARD, Last Name JONES, First Name MARY, Address Main St. 10, Block A, Apt. 5, London, Code 900B"
   Output: {"name": "JONES MARY", "address": "Main St. 10, Block A, Apt. 5, London"}

Now, extract the name and complete address from the following document:

{text}

Strict rules:
- Combine first and last name into a single "name" field
- Include street, number, building, apartment, district/county and city in address
- Ignore ALL identification numbers, postal codes, ID series or other codes
- Ignore nationality and other attributes that are not name
- If no address is provided, use "Not provided"
"""

PARTY_IDENTIFICATION_PROMPT = """
For a {contract_type} contract, assign roles to the following parties:

{pii_text}

Your task is to determine the roles of each person in the context of a {contract_type} contract.
Consider the instructions provided in the system prompt.

For each person, provide their name and ask the user what role they should have in the contract.
"""

CONTRACT_CONSTRUCTION_PROMPT = """Build a {contract_type} contract using the following template and verified information:

Template:
{template}

Verified parties: {parties_info}
Verified address: {address}
Additional details: {additional_info}
Object description: {object_description}

Instructions:
1. Use the provided template as the base for the contract
2. Insert verified party names directly into the contract without brackets
3. Use verified address for the 'Address' field in the contract
4. For buy-sell contracts:
   - Include payment details (advance and final payment) in the corresponding section
   - Include detailed object description in the 'Contract Object' section
5. Ensure all placeholders from the template are replaced with appropriate verified information
6. Use EXACTLY the provided roles for each party
7. If information is missing, leave the corresponding field empty or use a placeholder like [To be determined]
"""

SYSTEM_PROMPT = """
You are an AI assistant specialized in contract automation. Your task is to guide the process of information extraction, party identification, and contract building based on available data and templates.

Follow these instructions:

1. PII Extraction:
   Extract names, addresses, and any other relevant personal details from provided documents.

2. Party Identification:
   For each contract type, ask what role each person should have in the contract:
   - Buy-sell contract: Identify buyer and seller.
   - Airbnb contract: Identify owner (property owner) and tenant (guest).
   - IT contract: Identify IT consultant and client.

3. Contract Building:
   - Insert party names directly into contract without brackets.
   - Use provided addresses accurately in corresponding fields.
   - Ensure all placeholders from contract templates are replaced with correct information.
"""
