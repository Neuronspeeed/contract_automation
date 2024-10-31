<<<<<<< Updated upstream
class ContractRoleValidator:
    valid_roles = ["Landlord", "Tenant", "Buyer", "Seller", "Consultant", "Client"]
=======
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
            raise ValueError("Amount must be a valid number")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validates date format"""
        try:
            datetime.strptime(v, '%d/%m/%Y')
            return v
        except ValueError:
            raise ValueError("Date must be in DD/MM/YYYY format")

class ContractRoleValidator:
    """Validator for contract roles and types"""
    valid_roles = ["Owner", "Tenant", "Buyer", "Seller", "Consultant", "Client", "IT Consultant"]
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======

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
                amount=payment_details['advance'],
                date=payment_details['advance_date']
            )
            validator = PaymentValidator(
                amount=payment_details['final_payment'],
                date=payment_details['final_date']
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
            raise ValueError("Name must contain at least 3 characters")
        return v.title()

    @field_validator('address')
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validates address"""
        if len(v) < 5:
            raise ValueError("Address must contain at least 5 characters")
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
            raise ValueError("Contract content is too short")
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validates contract type"""
        return ContractRoleValidator.validate_contract_type(v)
>>>>>>> Stashed changes
