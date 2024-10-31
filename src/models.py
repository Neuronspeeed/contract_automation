from instructor import OpenAISchema, llm_validator
from pydantic import Field, BaseModel
from typing import List, Optional, Dict, Union, Any
from validators import ContractRoleValidator
from role_options import get_role_options
from openai_client import client


# Pydantic Models with llm_validator for enhanced validation
class PIIData(OpenAISchema):
    name: str = Field(..., description="Person's full name")
    address: str = Field(..., description="Person's residential address")

    async def validate_pii(self) -> bool:
        """Validate PII data with LLM."""
        if len(self.name) <= 3 or len(self.address) <= 5:
            return False
        
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if the following data is valid:\nName: {self.name}\nAddress: {self.address}"
            }],
            response_model=bool
        )
        return result

class ContractParty(OpenAISchema):
    name: str = Field(..., description="Party's name")
    roles: List[str] = Field(..., description="Party's roles in the contract")

    async def validate_roles(self) -> bool:
        """Validate roles with LLM."""
        if not all(role in ContractRoleValidator.valid_roles for role in self.roles):
            return False
            
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if roles {self.roles} are appropriate for person {self.name}"
            }],
            response_model=bool
        )
        return result

class ContractParties(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="List of parties involved in the contract")

    async def validate_parties(self) -> bool:
        """Validate parties with LLM."""
        if len(self.parties) < 2:
            return False
            
        parties_info = ", ".join([f"{party.name} ({', '.join(party.roles)})" for party in self.parties])
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if the following parties and their roles are assigned correctly:\n{parties_info}"
            }],
            response_model=bool
        )
        return result

class ContractDetails(OpenAISchema):
    contract_type: str = Field(..., description="Type of contract")
    additional_info: Dict[str, str] = Field(default_factory=dict)
    object_description: Optional[str] = Field(None)

    async def validate_contract_details(self) -> bool:
        """Validate contract details with LLM."""
        if not (self.contract_type.lower() in ContractRoleValidator.valid_types and 
                (self.object_description is None or len(self.object_description) > 10)):
            return False
            
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if the contract details are valid:\nType: {self.contract_type}\nDescription: {self.object_description}"
            }],
            response_model=bool
        )
        return result

class Contract(OpenAISchema):
    content: str = Field(..., description="Complete content of the contract")

    async def validate_content(self) -> bool:
        """Validate contract content with LLM."""
        if len(self.content) <= 100:
            return False
            
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if this contract contains all necessary sections:\n{self.content[:500]}..."
            }],
            response_model=bool
        )
        return result

# Define AgentAction before AgentState to avoid NameError
class AgentAction(OpenAISchema):
    action: str = Field(..., description="Action to be performed by the agent")
    reason: str = Field(..., description="Detailed reason for choosing this action")
    parameters: Dict[str, str] = Field(default_factory=dict)

    async def validate_action(self) -> bool:
        """Validate agent action with LLM."""
        if len(self.action) == 0 or len(self.reason) <= 10:
            return False
            
        result = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Verify if this action is valid:\nAction: {self.action}\nReason: {self.reason}"
            }],
            response_model=bool
        )
        return result

class AgentState(BaseModel):
    verified_pii_data: List[PIIData] = Field(default_factory=list, description="Verified PII data")
    contract_details: Optional[ContractDetails] = None
    parties: Optional[ContractParties] = None
    contract: Optional[Contract] = None
    data: Dict[str, Any] = Field(default_factory=dict, description="Dynamic data")
    history: List[AgentAction] = Field(default_factory=list, description="Agent's action history")

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
