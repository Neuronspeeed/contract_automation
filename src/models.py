from instructor import OpenAISchema
from pydantic import Field

class PIIData(OpenAISchema):
    name: str = Field(..., description="Full name of the person")
    address: str = Field(..., description="Residential address of the person")

class ContractParties(OpenAISchema):
    buyer: str = Field(..., description="Name of the buyer")
    seller: str = Field(..., description="Name of the seller")

class Contract(OpenAISchema):
    buyer: str = Field(..., description="Name of the buyer")
    seller: str = Field(..., description="Name of the seller")
    address: str = Field(..., description="Address where the contract is applicable")
    terms: str = Field(..., description="Terms of the contract")
