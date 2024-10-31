from typing import List

role_options = {
    "airbnb": ["Owner", "Tenant"],
    "buy-sell": ["Buyer", "Seller"],
    "it": ["Consultant", "Client"]
}

def get_role_options(contract_type: str) -> List[str]:
    """
    Get role options for a specific contract type.
    """
    return role_options.get(contract_type.lower(), [])
