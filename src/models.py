from instructor import OpenAISchema, llm_validator
from pydantic import Field, BaseModel, validator
from typing import List, Optional, Dict, Union, Any
from validators import ContractRoleValidator
from role_options import get_role_options

# Pydantic Models with llm_validator for enhanced validation
class PIIData(OpenAISchema):
    name: str = Field(..., description="Numele complet al persoanei")
    address: str = Field(..., description="Adresa de reședință a persoanei")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că datele PII sunt complete și exacte.", value)

class ContractParty(OpenAISchema):
    name: str = Field(..., description="Numele părții")
    roles: List[str] = Field(..., description="Rolurile părții în contract")

    @validator('roles', each_item=True)
    def validate_party_role(cls, v):
        return ContractRoleValidator.validate_role(v)

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că rolurile sunt valabile și potrivite pentru acest context. Pentru un contract Airbnb, 'Gazdă' este echivalent cu 'Proprietar', iar 'Oaspete' este echivalent cu 'Chiriaș'.", value)

class ContractParties(OpenAISchema):
    parties: List[ContractParty] = Field(..., description="Lista părților implicate în contract")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că părțile și rolurile sunt atribuite corect în contract.", value)

class ContractDetails(OpenAISchema):
    contract_type: str = Field(..., description="Tipul contractului (de exemplu, airbnb, cumpărare-vânzare, consultanță IT)")
    additional_info: Dict[str, str] = Field(default_factory=dict, description="Informații suplimentare specifice tipului contractului")

    @validator('contract_type')
    def validate_contract_type(cls, v):
        return ContractRoleValidator.validate_contract_type(v)

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că tipul contractului și detalile sunt corecte și corespund standardelor așteptate.", value)

class Contract(OpenAISchema):
    content: str = Field(..., description="Conținutul complet al contractului")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că contractul conține toate secțiunile necesare și urmează structura șablonului.", value)

# Define AgentAction before AgentState to avoid NameError
class AgentAction(OpenAISchema):
    action: str = Field(..., description="Acțiunea care urmează a fi efectuată de agent")
    reason: str = Field(..., description="Motivul detaliat pentru alegerea acestei acțiuni")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Parametrii acțiunii")

    class Config:
        arbitrary_types_allowed = True
        @classmethod
        def validate(cls, value):
            return llm_validator("Asigură-te că parametrii acțiunii sunt corecți și valabili pentru acțiunea dată.", value)

class AgentState(BaseModel):
    verified_pii_data: List[PIIData] = Field(default_factory=list, description="Date PII verificate")
    contract_details: Optional[ContractDetails] = None
    parties: Optional[ContractParties] = None
    contract: Optional[Contract] = None
    data: Dict[str, Any] = Field(default_factory=dict, description="Date dinamică")
    history: List['AgentAction'] = Field(default_factory=list, description="Istoricul acțiunilor agentului")  # Forward reference used here

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
