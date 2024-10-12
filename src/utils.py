from src.models import PIIData

def verify_information(pii: PIIData) -> bool:
    print(f"Please verify the following information:")
    print(f"Name: {pii.name}")
    print(f"Address: {pii.address}")
    verification = input("Is this information correct? (yes/no): ").lower()
    return verification == 'yes'
