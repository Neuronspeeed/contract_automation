from models import PIIData
from typing import List

def verify_information(pii_list: List[PIIData]) -> List[PIIData]:
    verified_pii_list = []
    for pii in pii_list:
        print(f"Please verify the following information:")
        print(f"Name: {pii.name}")
        print(f"Address: {pii.address}")
        verification = input("Is this information correct? (yes/no): ").lower()
        
        if verification == 'no':
            pii.name = input("Please provide the correct name: ")
            pii.address = input("Please provide the correct address: ")
        verified_pii_list.append(pii)
    return verified_pii_list