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
