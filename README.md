# Contract Automation System

## Overview

This project is an Agentic contract automation system that streamlines the process of creating contracts based on personal information and predefined templates. It uses OpenAI's an agent to extract information, identify parties, and construct contracts.

## Features

- Document processing and PII (Personally Identifiable Information) extraction
- Automatic contract type determination
- Party identification and role assignment
- Contract construction using templates
- Error handling and information verification

## Project Structure

- `src/`
  - `ai_functions.py`: Contains AI-powered functions for various tasks
  - `config.py`: Configuration settings and system prompts
  - `document_processing.py`: Functions for processing input documents
  - `main.py`: Main script orchestrating the contract creation process
  - `models.py`: Pydantic models for data structures
  - `utils.py`: Utility functions

## Key Functions

### AI Functions (`ai_functions.py`)

1. `extract_pii(text: str) -> List[PIIData]`:
   Extracts personal identifiable information from input text.

2. `identify_parties(pii_data: List[PIIData], contract_type: str) -> ContractParties`:
   Identifies parties and their roles based on extracted PII and contract type.

3. `determine_contract_details(parties: ContractParties, contract_type: str) -> ContractDetails`:
   Determines additional contract details based on parties and contract type.

4. `construct_contract(parties: ContractParties, address: str, template: str, details: ContractDetails) -> Contract`:
   Constructs a contract using provided information and a template.

5. `agent_action(state: AgentState, templates: Dict[str, Dict[str, str]]) -> AgentAction`:
   Determines the next action for the agent based on the current state.

### Main Process (`main.py`)

1. `process_pii_extraction(state: AgentState, documents: Dict[str, str]) -> None`:
   Processes documents and extracts PII.

2. `determine_contract_type(state: AgentState, templates: Dict[str, Dict]) -> None`:
   Determines the contract type based on user input.

3. `identify_contract_parties(state: AgentState) -> None`:
   Identifies contract parties and their roles.

4. `construct_final_contract(state: AgentState, templates: Dict[str, Dict[str, str]]) -> None`:
   Constructs the final contract using the gathered information and templates.

## Setup and Usage

This project uses Rye for dependency management and virtual environment setup.

1. Install Rye if you haven't already:
   ```
   curl -sSf https://rye-up.com/get | bash
   ```

2. Clone the repository:
   ```
   git clone https://github.com/yourusername/contract-automation.git
   cd contract-automation
   ```

3. Set up the project using Rye:
   ```
   rye sync
   ```

4. Set up your OpenAI API key in a `.env` file:
   ```
   echo "OPENAI_API_KEY=your_api_key_here" > .env
   ```

5. Run the main script:
   ```
   rye run python src/main.py
   ```

## Development

To add new dependencies:
