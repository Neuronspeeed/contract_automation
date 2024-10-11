from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Optional
from langchain_core.messages import BaseMessage

class PIIDataModel(BaseModel):
    name: str = Field(..., description="Full name of the person")
    address: str = Field(..., description="Residential address of the person")

    @model_validator(mode='before')
    def validate_non_empty(cls, values):
        for field in ['name', 'address']:
            if not values.get(field, "").strip():
                raise ValueError(f"Field '{field}' cannot be empty")
        return values

class ContractState(BaseModel):
    messages: List[BaseMessage] = Field(default_factory=list)
    extracted_texts: Dict[str, str] = Field(default_factory=dict)
    pii_data: Optional[List[Dict[str, PIIDataModel]]] = None
    address: Optional[str] = None
    extracted_text: Optional[str] = None
    buyer: Optional[str] = None
    seller: Optional[str] = None
    contract: Optional[str] = None

class ContractPartiesModel(BaseModel):
    buyer: str = Field(..., description="Full name of the buyer")
    seller: str = Field(..., description="Full name of the seller")

    @model_validator(mode='before')
    def validate_names(cls, values):
        for field in ['buyer', 'seller']:
            value = values.get(field)
            if value and not value.replace(' ', '').isalpha():
                raise ValueError(f"Field '{field}' must contain only alphabetic characters and spaces")
        return values