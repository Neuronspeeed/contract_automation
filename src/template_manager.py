from typing import Dict, List
import os

class TemplateManager:
    def __init__(self, templates: Dict[str, Dict[str, str]]):
        self.templates = templates

    def get_template(self, contract_type: str) -> str:
        """Retrieve the template based on the contract type."""
        template_key = f"{contract_type}.txt"  
        if template_key in self.templates:
            return self.templates[template_key]["content"]
        else:
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
