from datetime import datetime

class PaymentValidator:
    @staticmethod
    def validate_amount(amount: str) -> bool:
        try:
            float(amount.replace(',', '.'))
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_date(date_str: str) -> bool:
        try:
            datetime.strptime(date_str, '%d/%m/%Y')
            return True
        except ValueError:
            return False

class ContractRoleValidator:
    valid_roles = ["Proprietar", "Chiriaș", "Cumpărător", "Vânzător", "Consultant", "Client", "Consultant IT"]
    valid_types = ["airbnb", "vanzare-cumparare", "it"]

    @classmethod
    def validate_role(cls, role: str):
        if role not in cls.valid_roles:
            raise ValueError(f"Rol invalid: {role}. Trebuie să fie unul dintre {', '.join(cls.valid_roles)}")
        return role

    @classmethod
    def validate_contract_type(cls, contract_type: str):
        if contract_type.lower() not in cls.valid_types:
            raise ValueError(f"Tip de contract invalid: {contract_type}. Trebuie să fie unul dintre {', '.join(cls.valid_types)}")
        return contract_type.lower()

    @classmethod
    def validate_payment_details(cls, payment_details: dict) -> bool:
        validator = PaymentValidator()
        return all([
            validator.validate_amount(payment_details['avans']),
            validator.validate_date(payment_details['data_avans']),
            validator.validate_amount(payment_details['plata_finala']),
            validator.validate_date(payment_details['data_finala'])
        ])
