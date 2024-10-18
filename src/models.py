from instructor import OpenAISchema
from pydantic import Field, BaseModel
from typing import List, Optional, Dict, Union, Any

# PII data schema
class PIIData(OpenAISchema):
    name: str = Field(..., description="Full name of the person")
    address: str = Field(..., description="Residential address of the person")

# Contract party schema
class ContractParty(OpenAISchema):
    name: str = Field(..., description="Name of the party")
    roles: List[str] = Field(..., description="Roles of the party in the contract")

# Contract parties schema
class ContractParties(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")

# Contract schema
class Contract(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")
    address: str = Field(..., description="Address where the contract is applicable")
    terms: str = Field(..., description="Terms of the contract")

# Contract details schema
class ContractDetails(OpenAISchema):
    contract_type: str = Field(..., description="Type of contract (e.g., airbnb, buy-sell, it-consulting)")
    additional_info: Dict[str, str] = Field(default_factory=dict, description="Additional information specific to the contract type")

# Agent action schema
class AgentAction(OpenAISchema):
    action: str = Field(..., description="Action to be performed by the agent")
    reason: str = Field(..., description="Detailed reason for choosing this action")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Parameters for the action")

# Agent state schema
class AgentState(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict, description="Dynamic state data")
    history: List[AgentAction] = Field(default_factory=list, description="History of agent actions")

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

    @property
    def verified_pii_data(self) -> List[PIIData]:
        return self.get('verified_pii_data', [])

    @verified_pii_data.setter
    def verified_pii_data(self, value: List[PIIData]) -> None:
        self.update('verified_pii_data', value)

    @property
    def parties(self) -> Optional[ContractParties]:
        return self.get('parties')

    @parties.setter
    def parties(self, value: ContractParties) -> None:
        self.update('parties', value)

    @property
    def contract_details(self) -> Optional[ContractDetails]:
        return self.get('contract_details')

    @contract_details.setter
    def contract_details(self, value: ContractDetails) -> None:
        self.update('contract_details', value)

    @property
    def contract(self) -> Optional[Contract]:
        return self.get('contract')

    @contract.setter
    def contract(self, value: Contract) -> None:
        self.update('contract', value)

    @property
    def current_action(self) -> Optional[AgentAction]:
        return self.get_last_action()
