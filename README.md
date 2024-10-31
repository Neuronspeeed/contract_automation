# Contract Automation System

## Overview

This project is an Agentic contract automation system that streamlines the process of creating contracts based on personal information and predefined templates. It uses OpenAI's GPT model to extract information, identify parties, and construct contracts.






1. Prepare your documents:
   Place the documents you want to process (PDF, JPG, JPEG, PNG, or TXT files) in the `data` folder of the project.

2. Run the main script:
   """
   rye run python src/main.py
   """

3. Follow the prompts:
   - The system will extract PII (Personally Identifiable Information) from your documents.
   - Verify the extracted information when prompted.
   - Choose the type of contract you want to create.
   - Assign roles to the identified parties.
   - Review the constructed contract.

4. Output:
   The final contract will be displayed in the console. You can copy and save it as needed.

Note: Make sure you have set up your OpenAI API key in the `.env` file before running the script.
## Setup and Usage

This project uses Rye for dependency management and virtual environment setup.

1. Install Rye if you haven't already:
   """
   curl -sSf https://rye-up.com/get | bash
   """

2. Clone the repository:
   """
   git clone https://github.com/yourusername/contract-automation.git
   cd contract-automation
   """

3. Set up the project using Rye:
   """
   rye sync
   """

4. Set up your OpenAI API key in a `.env` file:
   """
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   """

5. Run the main script:
   """
   rye run python src/main.py
   """

## Development

To add new dependencies:

"""
rye add package_name
"""

To update dependencies:
"""
rye sync
"""

To run tests:
"""
rye run pytest
"""


## Chatbot Assistants - I added two different chatbot implementations separately from the agentic implementation.


### 1. OpenAI Assistant (Beta)
Uses OpenAI's Assistant API with built-in thread management and rate limiting:

rye run python src/chatbot/openai_assistant/client.py


### 2. Instructor-Enhanced Assistant
Uses OpenAI + Instructor for enhanced type validation and structured outputs:
## How to Use

rye run python src/chatbot/simple_run.py

Features:
- Strong type validation
- Structured data extraction
- Workflow state management
- Concurrent document processing




## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.