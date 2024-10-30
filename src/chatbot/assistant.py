from typing import Optional
import logging
from pathlib import Path
from openai_client import create_client
from models import ContractState, ContractResponse

logger = logging.getLogger(__name__)

class ContractAssistant:
    def __init__(self, api_key: str):
        self.client = create_client(api_key)
        self.state = ContractState()
        self.upload_dir = Path("uploads/id_images")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def process_workflow(self) -> None:
        """Main workflow for contract processing."""
        try:
            # Stage 1: Get contract type
            await self.process_contract_type()
            
            # Stage 2: Attach ID images
            await self.attach_id_images()
            
            # Stage 3: Get phone information
            await self.collect_phone_info()
            
            print("\nProcesul a fost finalizat cu succes!")
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            raise

    async def process_message(self, message: str) -> str:
        """Process user message through OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                response_model=ContractResponse,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": message},
                    {"role": "assistant", "content": self._get_context()}
                ]
            )
            
            await self._handle_response(response)
            return response.message
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise

    async def _handle_response(self, response: ContractResponse) -> None:
        """Handle the AI response and update state accordingly."""
        if response.next_action == "get_contract" and response.extracted_data:
            self.state.contract_type = response.extracted_data
            await self.process_contract_type()
        elif response.next_action == "attach_id":
            await self.attach_id_images()
        elif response.next_action == "get_phone" and response.extracted_data:
            if await self.state.validate_phone(response.extracted_data):
                self.state.phone_numbers.append(response.extracted_data)

    def _get_system_prompt(self) -> str:
        return """
        Ești un asistent specializat în colectarea informațiilor despre contracte.
        
        1. Determina tipul de contract:
            - airbnb
            - vanzare-cumparare
            - consultanta IT
        2. Colectează cărțile de identitate și numerele de telefon.
        3. Fii concis și direct în răspunsurile tale"""

    def _get_context(self) -> str:
        return f"""Stare curentă:
Contract: {self.state.contract_type or 'Nedeterminat'}
ID-uri atașate: {len(self.state.id_images)}
Telefoane colectate: {len(self.state.phone_numbers)}"""
