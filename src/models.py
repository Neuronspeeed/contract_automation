from instructor import OpenAISchema, llm_validator
from pydantic import Field, BaseModel, validator
from typing import List, Optional, Dict, Union, Any

# Centralized Role Options
role_options = {
    "airbnb": ["Landlord", "Tenant"],
    "buy-sell": ["Buyer", "Seller"],
    "it": ["Consultant", "Client"]
}

def get_role_options(contract_type: str) -> List[str]:
    """
    Retrieve role options for a given contract type.
    """
    return role_options.get(contract_type.lower(), [])

# Validator class for roles and contract types
class ContractRoleValidator:
    valid_roles = ["Landlord", "Tenant", "Buyer", "Seller", "Consultant", "Client"]
    valid_types = ["airbnb", "buy-sell", "it"]

    @classmethod
    def validate_role(cls, role: str):
        if role not in cls.valid_roles:
            raise ValueError(f"Invalid role: {role}. Must be one of {', '.join(cls.valid_roles)}")
        return role

    @classmethod
    def validate_contract_type(cls, contract_type: str):
        if contract_type.lower() not in cls.valid_types:
            raise ValueError(f"Invalid contract type: {contract_type}. Must be one of {', '.join(cls.valid_types)}")
        return contract_type.lower()

# Pydantic Models with llm_validator for enhanced validation
class PIIData(OpenAISchema):
    name: str = Field(..., description="Full name of the person")
    address: str = Field(..., description="Residential address of the person")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the PII data is complete and accurate.", value)

class ContractParty(OpenAISchema):
    name: str = Field(..., description="Name of the party")
    roles: List[str] = Field(..., description="Roles of the party in the contract")

    @validator('roles', each_item=True)
    def validate_party_role(cls, v):
        return ContractRoleValidator.validate_role(v)

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the roles are valid and appropriate for this context.", value)

class ContractParties(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the parties and roles are correctly assigned in the contract.", value)

class ContractDetails(OpenAISchema):
    contract_type: str = Field(..., description="Type of contract (e.g., airbnb, buy-sell, it-consulting)")
    additional_info: Dict[str, str] = Field(default_factory=dict, description="Additional information specific to the contract type")

    @validator('contract_type')
    def validate_contract_type(cls, v):
        return ContractRoleValidator.validate_contract_type(v)

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the contract type and details are correct and match the expected standards.", value)

class Contract(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")
    address: str = Field(..., description="Address where the contract is applicable")
    terms: str = Field(..., description="Terms of the contract")
    additional_info: str

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the contract contains all required parties, details, and addresses.", value)

# Define AgentAction before AgentState to avoid NameError
class AgentAction(OpenAISchema):
    action: str = Field(..., description="Action to be performed by the agent")
    reason: str = Field(..., description="Detailed reason for choosing this action")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Parameters for the action")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Ensure that the agent action parameters are correct and valid for the given action.", value)

class AgentState(BaseModel):
    verified_pii_data: List[PIIData] = Field(default_factory=list, description="Verified PII data")
    contract_details: Optional[ContractDetails] = None
    parties: Optional[ContractParties] = None
    contract: Optional[Contract] = None
    data: Dict[str, Any] = Field(default_factory=dict, description="Dynamic state data")
    history: List['AgentAction'] = Field(default_factory=list, description="History of agent actions")  # Forward reference used here

    def update(self, key: str, value: Any) -> None:
        """Update a specific key in the state data."""
        self.data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the state data."""
        return self.data.get(key, default)

    def add_action(self, action: AgentAction) -> None:
        """Add an action to the history."""
        self.history.append(action)

    def get_last_action(self) -> Optional[AgentAction]:
        """Get the last action from the history."""
        return self.history[-1] if self.history else None

    def clear(self) -> None:
        """Clear the state data and history."""
        self.data.clear()
        self.history.clear()
