# Contract Automation System

## Overview
This project is an Agentic contract automation system that streamlines contract creation, legal research, and GDPR compliance analysis using AI. It combines multiple specialized agents and assistants to provide comprehensive contract management solutions.

## Features

### 1. Contract Automation
- PII extraction from documents
- Party identification and role assignment
- Template-based contract generation
- Document processing (PDF, JPG, JPEG, PNG, TXT)

### 2. Legal Research Agent
- Automated legal research using Tavily API
- GDPR compliance analysis
- ReAct prompting for structured reasoning
- Automated insights generation

### 3. Chatbot Assistants
#### OpenAI Assistant (Beta)
- Built-in thread management
- Rate limiting
- Interactive contract guidance

#### Instructor-Enhanced Assistant
- Strong type validation
- Structured data extraction
- Workflow state management

## Setup

1. Install Rye:
   """
   curl -sSf https://rye-up.com/get | bash
   """

2. Clone and setup:
   """
   git clone https://github.com/yourusername/contract-automation.git
   cd contract-automation
   rye sync
   """

3. Environment setup:
   """
   # Create .env file with your API keys
   OPENAI_API_KEY=your_api_key_here
   TAVILY_API_KEY=your_tavily_key_here
   """

## Usage

### Contract Automation
"""
rye run python src/main.py
"""

### Legal Research
"""
rye run python src/legalsearch/agent_legal_search.py
"""

### Chatbot Assistants
"""
# OpenAI Assistant
rye run python src/chatbot/openai_assistant/client.py

# Instructor-Enhanced Assistant
rye run python src/chatbot/simple_run.py
"""

## Development

### Dependencies
"""
# Add new dependencies
rye add package_name

# Update dependencies
rye sync

# Run tests
rye run pytest
"""

## Contributing
Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.