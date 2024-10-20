from typing import Dict, List

class TemplateManager:
    def __init__(self, templates: Dict[str, Dict[str, str]]):
        self.templates = templates

    def get_template(self, contract_type: str) -> str:
        """Retrieve the template based on the contract type."""
        # Adjust the expected filename based on your naming convention
        template_key = f"{contract_type}.consulting.txt"  # Assuming this is the correct format
        return self.templates.get(template_key, None)

    def list_available_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
