from typing import Optional, Dict, List
import logging
from pathlib import Path
import instructor
from openai import AsyncOpenAI
from models import ContractState, ContractResponse, AgentAction
import asyncio

logger = logging.getLogger(__name__)

class ContractAssistant:
    def __init__(self, api_key: str):
        self.client = instructor.patch(AsyncOpenAI(api_key=api_key))
        self.state = ContractState()
        self.upload_dir = Path("uploads/id_images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Define workflow stages
        self.workflow_stages = {
            "init": self._process_contract_type,
            "get_contract": self._process_documents,
            "attach_id": self._process_identities,
            "get_phone": self._process_contact,
            "complete": self._finalize_contract
        }

    async def process_message(self, message: str) -> str:
        """Process user message and execute workflow stage."""
        try:
            # Get AI response and next action
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=ContractResponse,
                messages=self._build_context(message)
            )
            
            # Execute workflow stage if we have data
            if response.extracted_data:
                stage_handler = self.workflow_stages.get(self.state.step)
                if stage_handler:
                    await stage_handler(response.extracted_data)
            
            return response.message
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            raise

    async def _process_contract_type(self, data: str) -> None:
        """Process contract type selection."""
        if data in ["airbnb", "buy-sell", "it consulting"]:
            self.state.details.contract_type = data
            self.state.step = "get_contract"
            logger.info(f"Contract type set to: {data}")

    async def _process_documents(self, documents: List[str]) -> None:
        """Process document uploads concurrently."""
        tasks = [self.state.validate_image(doc) for doc in documents]
        results = await asyncio.gather(*tasks)
        
        for document, valid in zip(documents, results):
            if valid:
                self.state.id_images.append(document)
                logger.info(f"Document added: {document}")

        if len(self.state.id_images) >= 2:
            self.state.step = "attach_id"
            logger.info("Document processing complete. Moving to identity attachment stage.")

    async def _process_identities(self, identities: List[str]) -> None:
        """Process identity information concurrently."""
        tasks = [self._validate_identity(identity) for identity in identities]
        await asyncio.gather(*tasks)
        self.state.step = "get_phone"
        logger.info("Identity processing complete. Moving to contact information stage.")

    async def _validate_identity(self, identity: str) -> None:
        """Simulate identity validation."""
        logger.info(f"Validating identity: {identity}")
        await asyncio.sleep(1)

    async def _process_contact(self, contact_info: List[str]) -> None:
        """Process contact information."""
        tasks = [self._validate_contact_data(contact) for contact in contact_info]
        results = await asyncio.gather(*tasks)

        for contact, valid in zip(contact_info, results):
            if valid:
                await self._store_contact_data(contact)

        if len(self.state.phone_numbers) >= 1:
            self.state.step = "complete"
            logger.info("Contact processing complete. Ready to finalize.")

    async def _validate_contact_data(self, contact: str) -> bool:
        """Validate contact information."""
        logger.info(f"Validating contact: {contact}")
        await asyncio.sleep(1)
        return True

    async def _store_contact_data(self, contact: str) -> None:
        """Store valid contact information."""
        self.state.phone_numbers.append(contact)
        logger.info(f"Contact added: {contact}")

    async def _finalize_contract(self, data: str) -> None:
        """Finalize contract processing."""
        if self.state.is_complete():
            logger.info("Contract processing complete.")

    def _build_context(self, message: str) -> List[Dict[str, str]]:
        """Build message context for AI."""
        return [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": message},
            {"role": "assistant", "content": self._get_context()}
        ]

    def _get_system_prompt(self) -> str:
        return """
        You are an agent specialized in contract processing. Guide the user through the following steps:

        1. CONTRACT DETERMINATION
        - Identify desired contract type (airbnb/buy-sell/it consulting)
        - Extract information from conversation or ask explicitly

        2. DOCUMENT COLLECTION
        - Request ID documents from involved parties
        - Verify valid format (.png, .jpg, .jpeg)
        - Minimum 2 documents required

        3. CONTACT INFORMATION
        - Collect phone numbers
        - Validate number format
        - Minimum one number required

        4. FINALIZATION
        - Verify all information is complete
        - Confirm with user

        Respond naturally and guide the user step by step.
        Extract and validate provided information.
        """

    def _get_context(self) -> str:
        return f"""Current State:
Contract: {self.state.details.contract_type or 'Undetermined'}
Attached IDs: {len(self.state.id_images)}
Collected Phones: {len(self.state.phone_numbers)}"""