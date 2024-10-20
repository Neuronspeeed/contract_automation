import os
import asyncio
import aiofiles
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader

import easyocr
from config import DATA_FOLDER

# Initialize EasyOCR reader
reader = easyocr.Reader(['en', 'ro'])

# Get documents from the data folder
def get_documents() -> List[str]:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    all_files = os.listdir(DATA_FOLDER)
    documents = [
        os.path.join(DATA_FOLDER, f)
        for f in all_files
        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt'))
    ]
    return documents

# Extract text from a file
async def extract_text(file_path: str) -> str:
    if file_path.lower().endswith('.pdf'):
        try:
            loader = PyPDFLoader(file_path)
            pages = await asyncio.to_thread(loader.load)
            return "\n".join(page.page_content for page in pages)
        except ImportError:
            return "Error: PyPDFLoader not available. Please install langchain."
    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            def process_image():
                results = reader.readtext(file_path)
                return ' '.join([result[1] for result in results])
            return await asyncio.to_thread(process_image)
        except Exception as e:
            return f"Error processing image: {str(e)}"
    else:
        try:
            async with aiofiles.open(file_path, mode='r') as f:
                return await f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
async def process_documents() -> Dict[str, str]:
    documents = get_documents()
    results = {}
    for doc in documents:
        try:
            text = await extract_text(doc)
            results[os.path.basename(doc)] = text
        except Exception as e:
            results[os.path.basename(doc)] = f"Error processing file: {str(e)}"
    return results

# Load templates from the specified folder
def load_templates(folder_path: str) -> Dict[str, Dict[str, str]]:
    templates = {}
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                content = file.read()
                
                # Extract metadata from the first few lines (e.g., lines starting with "#")
                metadata = {}
                lines = content.splitlines()
                body_start = 0
                for i, line in enumerate(lines):
                    if line.startswith("#"):
                        key, _, value = line[1:].partition(":")
                        metadata[key.strip()] = value.strip()
                    else:
                        body_start = i
                        break

                template_body = "\n".join(lines[body_start:])
                templates[filename] = {"metadata": metadata, "content": template_body}
    return templates
