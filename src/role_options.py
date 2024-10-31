from typing import List

role_options = {
<<<<<<< Updated upstream
    "airbnb": ["Landlord", "Tenant"],
=======
    "airbnb": ["Owner", "Tenant"],
>>>>>>> Stashed changes
    "buy-sell": ["Buyer", "Seller"],
    "it": ["Consultant", "Client"]
}

def get_role_options(contract_type: str) -> List[str]:
    """
<<<<<<< Updated upstream
    Retrieve role options for a given contract type.
=======
    Get role options for a specific contract type.
>>>>>>> Stashed changes
    """
    return role_options.get(contract_type.lower(), [])
