from typing import List

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
