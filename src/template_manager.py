from typing import Dict, List
import os

class TemplateManager:
    def __init__(self, templates: Dict[str, Dict[str, str]]):
        self.templates = templates

    def get_template(self, contract_type: str) -> str:
        """Recuperează șablonul bazat pe tipul contractului."""
        contract_type = contract_type.lower()
        for template_key in self.templates.keys():
            if contract_type in template_key.lower():
                return self.templates[template_key]["content"]
        if contract_type == "vanzare-cumparare":
            return self.templates["buy-sell.txt"]["content"]
        raise FileNotFoundError(f"Nu s-a găsit niciun șablon pentru {contract_type}. Șabloane disponibile: {', '.join(self.templates.keys())}")

    def list_available_templates(self) -> List[str]:
        """Listează toate numele de șabloane disponibile."""
        return list(self.templates.keys())

def load_templates(folder_path: str) -> Dict[str, Dict[str, str]]:
    templates = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
                content = file.read()
                templates[filename] = {"content": content}
    print(f"Șabloane încărcate: {templates.keys()}")  
    return templates