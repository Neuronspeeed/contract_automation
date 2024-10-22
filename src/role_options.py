from typing import List

role_options = {
    "airbnb": ["Proprietar", "Chiriaș"],
    "vanzare-cumparare": ["Cumpărător", "Vânzător"],
    "it": ["Consultant", "Client"]
}

def get_role_options(contract_type: str) -> List[str]:
    """
    Recuperează opțiunile de rol pentru un anumit tip de contract.
    """
    return role_options.get(contract_type.lower(), [])
