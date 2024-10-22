class ContractRoleValidator:
    valid_roles = ["Proprietar", "Chiriaș", "Cumpărător", "Vânzător", "Consultant", "Client"]
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
