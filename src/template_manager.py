from typing import Dict, List
import os

class TemplateManager:
    def __init__(self, templates: Dict[str, Dict[str, str]]):
        self.templates = templates

    def get_template(self, contract_type: str) -> str:
        """Get template based on contract type."""
        contract_type = contract_type.lower()
        for template_key in self.templates.keys():
            if contract_type.lower() in template_key.lower():
                return self.templates[template_key]["content"]
        if contract_type == "buy-sell":
            return self.templates["buy-sell.txt"]["content"]
        raise FileNotFoundError(f"No template found for {contract_type}. Available templates: {', '.join(self.templates.keys())}")

    def list_available_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())

def load_templates(folder_path: str) -> Dict[str, Dict[str, str]]:
    templates = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                content = file.read()
                templates[filename] = {"content": content}
    print(f"Loaded templates: {templates.keys()}")  
    return templates
