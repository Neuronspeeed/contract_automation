from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, field_validator

class ContractState(MessagesState):
    pii_data: dict = Field(default_factory=dict)
    address: str = ""
    buyer: str = ""
    seller: str = ""
    contract: str = ""
    extracted_text: str = ""
    extracted_texts: dict = Field(default_factory=dict)

class PiiDataModel(BaseModel):
    name: str
    address: str

    @field_validator("name", "address")
    def validate_fields(cls, value):
        if not value:
            raise ValueError("Field cannot be empty")
        return value

class ContractPartiesModel(BaseModel):
    buyer: str
    seller: str

    @field_validator("buyer", "seller")
    def validate_names(cls, value):
        if not value.isalpha():
            raise ValueError("Name must contain only alphabetic characters")
        return value