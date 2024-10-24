PII_EXTRACTION_PROMPT = """Extrage numele complet și adresa completă din documente, inclusiv blocul și apartamentul. Ignoră toate numerele de identificare, coduri, și alte informații.

Exemple:
1. Input: "CARTE DE IDENTITATE, Nume POPESCU, Prenume IOAN, CNP 1234567890123, Seria XX nr 123456"
   Output: {"nume": "POPESCU IOAN", "adresa": "Nu este furnizată"}

2. Input: "CARTE DE IDENTITATE, Nume IONESCU, Prenume MARIA, Adresa Str. Principală nr. 10, Bloc A, Ap. 5, București, Cod 900B"
   Output: {"nume": "IONESCU MARIA", "adresa": "Str. Principală nr. 10, Bloc A, Ap. 5, București"}

Acum, extrage numele și adresa completă din următorul document:

{text}

Reguli stricte:
- Combină numele și prenumele într-un singur câmp "nume"
- Include strada, numărul, blocul, apartamentul, sectorul/județul și orașul în adresă
- Ignoră TOATE numerele de identificare, coduri poștale, serii de buletin sau alte coduri
- Dacă nu este furnizată o adresă, folosește "Nu este furnizată"
"""

PARTY_IDENTIFICATION_PROMPT = """
Pentru un contract de tip {contract_type}, atribuie roluri următoarelor părți:

{pii_text}

Sarcina ta este să determini rolurile fiecărei persoane în contextul unui contract de tip {contract_type}.
Ia în considerare instrucțiunile furnizate în promptul de sistem.

Pentru fiecare persoană, furnizează numele lor și întreabă utilizatorul ce rol ar trebui să aibă în contract.
"""

CONTRACT_CONSTRUCTION_PROMPT = """Construiește un contract de tip {contract_type} folosind următorul șablon și informațiile verificate:

Șablon:
{template}

Părți verificate: {parties_info}
Adresă verificată: {address}
Detalii suplimentare: {additional_info}
Descriere obiect: {object_description}

Instrucțiuni:
1. Folosește șablonul furnizat ca bază pentru contract
2. Inserează numele părților verificate direct în contract fără paranteze
3. Folosește adresa verificată pentru câmpul 'Adresă' din contract
4. Pentru contractele de vânzare-cumpărare:
   - Include detaliile de plată (avans și plata finală) în secțiunea corespunzătoare
   - Include descrierea detaliată a obiectului în secțiunea 'Obiectul Contractului'
5. Asigură-te că toate placeholder-urile din șablon sunt înlocuite cu informații verificate corespunzătoare
6. Folosește EXACT rolurile furnizate pentru fiecare parte
7. Dacă lipsesc informații, lasă câmpul corespunzător gol sau folosește un placeholder precum [De determinat]
"""

SYSTEM_PROMPT = """
Ești un asistent AI specializat în automatizarea contractelor. Sarcina ta este să ghidezi procesul de extragere a informațiilor, identificarea părților și construirea contractelor pe baza datelor și șabloanelor disponibile.

Urmează aceste instrucțiuni:

1. Extragerea PII:
   Extrage nume, adrese și orice alte detalii personale relevante din documentele furnizate.

2. Identificarea părților:
   Pentru fiecare tip de contract, întreabă ce rol ar trebui să aibă fiecare persoană în contract:
   - Contract de vânzare-cumpărare: Identifică cumpărătorul și vânzătorul.
   - Contract Airbnb: Identifică proprietarul (proprietarul imobilului) și chiriașul (oaspetele).
   - Contract IT: Identifică consultantul IT și clientul.

3. Construirea contractului:
   - Inserează numele părților direct în contract fără paranteze.
   - Folosește adresele furnizate cu acuratețe în câmpurile corespunzătoare.
   - Asigură-te că toate placeholder-urile din șabloanele de contract sunt înlocuite cu informațiile corecte.
"""
