from instructor import OpenAISchema
from pydantic import Field
from typing import List, Optional, Dict, Union

class PIIData(OpenAISchema):
    name: str = Field(..., description="Full name of the person")
    address: str = Field(..., description="Residential address of the person")

class ContractParty(OpenAISchema):
    name: str = Field(..., description="Name of the party")
    role: str = Field(..., description="Role of the party in the contract")

class ContractParties(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")

class Contract(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")
    address: str = Field(..., description="Address where the contract is applicable")
    terms: str = Field(..., description="Terms of the contract")

class ContractDetails(OpenAISchema):
    contract_type: str = Field(..., description="Type of contract (e.g., airbnb, buy-sell, it-consulting)")
    additional_info: Dict[str, str] = Field(default_factory=dict, description="Additional information specific to the contract type")

class AgentAction(OpenAISchema):
    action: str = Field(..., description="Action to be performed by the agent")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Parameters for the action")

class AgentState(OpenAISchema):
    verified_pii_data: List[PIIData] = Field(default_factory=list)
    parties: Optional[ContractParties] = None
    contract_details: Optional[ContractDetails] = None
    contract: Optional[Contract] = None
    current_action: Optional[AgentAction] = None
