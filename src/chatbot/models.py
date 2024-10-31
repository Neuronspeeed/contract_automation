from instructor import OpenAISchema
from typing import Optional, List, Dict, Literal
from pydantic import Field
from openai import AsyncOpenAI
from pathlib import Path

class ContractParty(OpenAISchema):
    """Information about a contract party."""
    name: str = Field(..., description="Party's full name")
    role: str = Field(..., description="Role in contract (e.g., seller, buyer)")
    phone: Optional[str] = Field(None, description="Phone number")
    id_image: Optional[str] = Field(None, description="Path to ID image")

class ContractDetails(OpenAISchema):
    """Details about the contract."""
    contract_type: Optional[Literal["airbnb", "buy-sell", "it"]] = Field(
        None, description="Contract type"
    )
    parties: List[ContractParty] = Field(default_factory=list)
    additional_info: Dict[str, str] = Field(default_factory=dict)

class AgentAction(OpenAISchema):
    """Action to be taken by the agent."""
    action: str = Field(..., description="Action to be taken")
    reason: str = Field(..., description="Reason for this action")
    parameters: Dict[str, str] = Field(default_factory=dict)

    async def validate(self) -> bool:
        """Validate if the action is reasonable."""
        return len(self.action) > 0 and len(self.reason) > 10

class ContractResponse(OpenAISchema):
    """Response from the AI assistant."""
    message: str = Field(..., description="Message for user")
    next_action: AgentAction = Field(..., description="Next action")
    extracted_data: Optional[Dict[str, str]] = Field(None, description="Extracted data")

class ContractState(OpenAISchema):
    """Current state of the contract processing."""
    step: Literal["init", "get_contract", "attach_id", "get_phone", "complete"] = Field(
        default="init"
    )
    details: ContractDetails = Field(default_factory=ContractDetails)
    current_party: Optional[ContractParty] = Field(None)
    id_images: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    
    async def validate_image(self, image_path: str) -> bool:
        """Validate if file exists and is an image."""
        path = Path(image_path)
        return (
            path.exists() and 
            path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        )

    def is_complete(self) -> bool:
        """Check if all required data is present."""
        return bool(
            self.details.contract_type and
            len(self.details.parties) >= 2 and
            all(p.phone for p in self.details.parties) and
            all(p.id_image for p in self.details.parties)
        )

    def add_party(self, party: ContractParty) -> None:
        """Add a party to the contract."""
        self.details.parties.append(party)
        self.current_party = None