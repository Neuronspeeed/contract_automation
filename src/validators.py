from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError, field_validator
from typing_extensions import Annotated
from pydantic.functional_validators import AfterValidator, BeforeValidator

class PaymentValidator(BaseModel):
    """Validator for payment-related fields"""
    amount: Annotated[str, BeforeValidator(lambda x: str(x).replace(',', '.'))]
    date: str

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: str) -> str:
        """Validates payment amount format"""
        try:
            float(v)
            return v
        except ValueError:
            raise ValueError("Suma trebuie să fie un număr valid")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validates date format"""
        try:
            datetime.strptime(v, '%d/%m/%Y')
            return v
        except ValueError:
            raise ValueError("Data trebuie să fie în formatul DD/MM/YYYY")

class ContractRoleValidator:
    """Validator for contract roles and types"""
    valid_roles = ["Proprietar", "Chiriaș", "Cumpărător", "Vânzător", "Consultant", "Client", "Consultant IT"]
    valid_types = ["airbnb", "vanzare-cumparare", "it"]

    @classmethod
    def validate_role(cls, role: str) -> str:
        """
        Validates if a role is allowed.
        
        Args:
            role: The role to validate
            
        Returns:
            str: The validated role
            
        Raises:
            ValueError: If role is invalid
        """
        if role not in cls.valid_roles:
            raise ValueError(f"Rol invalid: {role}. Trebuie să fie unul dintre {', '.join(cls.valid_roles)}")
        return role

    @classmethod
    def validate_contract_type(cls, contract_type: str) -> str:
        """
        Validates if a contract type is allowed.
        
        Args:
            contract_type: The contract type to validate
            
        Returns:
            str: The validated contract type
            
        Raises:
            ValueError: If contract type is invalid
        """
        if contract_type.lower() not in cls.valid_types:
            raise ValueError(f"Tip de contract invalid: {contract_type}. Trebuie să fie unul dintre {', '.join(cls.valid_types)}")
        return contract_type.lower()

    @classmethod
    def validate_payment_details(cls, payment_details: Dict[str, Any]) -> bool:
        """
        Validates payment details for a contract.
        
        Args:
            payment_details: Dictionary containing payment information
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            validator = PaymentValidator(
                amount=payment_details['avans'],
                date=payment_details['data_avans']
            )
            validator = PaymentValidator(
                amount=payment_details['plata_finala'],
                date=payment_details['data_finala']
            )
            return True
        except (ValidationError, KeyError):
            return False

class PIIValidator(BaseModel):
    """Validator for Personally Identifiable Information"""
    name: Annotated[str, AfterValidator(lambda x: x.strip())]
    address: Annotated[str, AfterValidator(lambda x: x.strip())]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validates person name"""
        if len(v) < 3:
            raise ValueError("Numele trebuie să conțină cel puțin 3 caractere")
        return v.title()

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validates address"""
        if len(v) < 5:
            raise ValueError("Adresa trebuie să conțină cel puțin 5 caractere")
        return v

class ContractValidator(BaseModel):
    """Validator for contract content"""
    content: str
    type: str
    parties: Dict[str, str]

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validates contract content"""
        if len(v) < 100:
            raise ValueError("Conținutul contractului este prea scurt")
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validates contract type"""
        return ContractRoleValidator.validate_contract_type(v)
