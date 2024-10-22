from models import PIIData
from typing import List

def verify_information(pii_list: List[PIIData]) -> List[PIIData]:
    verified_pii_list = []
    for pii in pii_list:
        print(f"Vă rugăm să verificați următoarele informații:")
        print(f"Nume: {pii.name}")
        print(f"Adresă: {pii.address}")
        verification = input("Aceste informații sunt corecte? (da/nu): ").lower()
        
        if verification == 'nu':
            pii.name = input("Vă rugăm să furnizați numele corect: ")
            pii.address = input("Vă rugăm să furnizați adresa corectă: ")
        verified_pii_list.append(pii)
    return verified_pii_list
