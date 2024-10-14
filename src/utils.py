from models import PIIData

def verify_information(pii: PIIData) -> PIIData:
    print(f"Please verify the following information:")
    print(f"Name: {pii.name}")
    print(f"Address: {pii.address}")
    verification = input("Is this information correct? (yes/no): ").lower()
    
    if verification == 'no':
        pii.name = input("Please provide the correct name: ")
        pii.address = input("Please provide the correct address: ")
    return pii
