<<<<<<< Updated upstream
PII_EXTRACTION_PROMPT = """Extract personal identifiable information (PII) from documents.

Examples:
1. Input: "CARTE DE IDENTITATE, Nume/Nom/Last name POPESCU, Prenume/Prénom/First name IOAN, CNP 1234567890123"
   Output: {"name": "POPESCU IOAN", "address": "Not provided"}

2. Input: "IDENTITY CARD, Last name SMITH, First name JOHN, Address 123 Main St, New York, NY 10001"
   Output: {"name": "SMITH JOHN", "address": "123 Main St, New York, NY 10001"}

3. Input: "CARTE D'IDENTITE, Nom DUPONT, Prénom MARIE, Adresse 1 Rue de la Paix, Paris 75001"
   Output: {"name": "DUPONT MARIE", "address": "1 Rue de la Paix, Paris 75001"}

Now, extract the PII from the following document:

{text}

Remember:
- Combine last name and first name into a single "name" field.
- If an address is not provided, use "Not provided" for the address field.
- Ignore any identification numbers or codes.
=======
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
>>>>>>> Stashed changes
"""

PARTY_IDENTIFICATION_PROMPT = """
For a {contract_type} contract, assign roles to the following parties:

{pii_text}

Your task is to determine the roles of each person in the context of a {contract_type} contract.
<<<<<<< Updated upstream
Consider the guidelines provided in the system prompt.

For each person, provide their name and ask the human which role they should have in the contract.
"""

CONTRACT_CONSTRUCTION_PROMPT = """Construct a {contract_type} contract using the following template and verified information:
=======
Consider the instructions provided in the system prompt.

For each person, provide their name and ask the user what role they should have in the contract.
"""

CONTRACT_CONSTRUCTION_PROMPT = """Build a {contract_type} contract using the following template and verified information:
>>>>>>> Stashed changes

Template:
{template}

<<<<<<< Updated upstream
Verified Parties: {parties_info}
Verified Address: {address}
Additional Details: {additional_info}

Instructions:
1. Use the provided template as a base for the contract.
2. Insert the verified parties' names directly into the contract without brackets.
3. Use the verified address for the 'Address' field in the contract.
4. Ensure all placeholders in the template are replaced with appropriate verified information.
5. Use the EXACT roles provided for each party (e.g., "Landlord" and "Tenant" for Airbnb contracts, not "Host" and "Guest").
6. If any information is missing, leave the corresponding field blank or use a placeholder like [To be determined].
"""

SYSTEM_PROMPT = """
You are an AI assistant specialized in contract automation. Your task is to guide the process of extracting information, identifying parties, and constructing contracts based on the available data and templates.

Follow these guidelines:

1. PII Extraction:
   Extract names, addresses, and any other relevant personal details from the provided documents.

2. Party Identification:
   For each contract type, ask which role each person should have in the contract:
   - Buy-sell contract: Identify the buyer and the seller.
   - Airbnb contract: Identify the landlord (property owner) and the tenant (guest).
   - IT contract: Identify the IT consultant and the client.

3. Contract Construction:
   - Insert party names directly into the contract without brackets.
   - Use the provided addresses accurately in the appropriate fields.
   - Ensure all placeholders in contract templates are replaced with the correct information.
=======
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
>>>>>>> Stashed changes
"""
