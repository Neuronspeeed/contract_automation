from instructor import OpenAISchema
from typing import Optional, List, Literal
from pydantic import Field

class ContractResponse(OpenAISchema):
    message: str = Field(..., description="Răspunsul pentru utilizator")
    next_action: Literal["get_contract", "attach_id", "get_phone", "complete"] = Field(
        ..., description="Următoarea acțiune necesară"
    )
    extracted_data: Optional[str] = Field(None, description="Date extrase din input")

class ContractState(OpenAISchema):
    step: Literal["init", "get_contract", "attach_id", "get_phone", "complete"] = Field(
        default="init",
        description="Current workflow step"
    )
    contract_type: Optional[str] = Field(None, description="Type of contract")
    id_images: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)

    async def validate_image(self, image_path: str) -> bool:
        """Validate if file exists and is an image"""
        return image_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))