import os
import asyncio
import aiofiles
from typing import List, Dict
from langchain.document_loaders import PyPDFLoader
import easyocr
from config import DATA_FOLDER

# Initialize EasyOCR reader
reader = easyocr.Reader(['en', 'ro'])

def get_documents() -> List[str]:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    all_files = os.listdir(DATA_FOLDER)
    documents = [
        os.path.join(DATA_FOLDER, f)
        for f in all_files
        if f.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.txt'))
    ]
    print(f"Total files in {DATA_FOLDER}: {len(all_files)}")
    if all_files:
        print(f"Files found: {all_files}")
        print(f"Documents to process: {len(documents)}")
        if not documents:
            print("Warning: No files with supported extensions (.pdf, .jpg, .jpeg, .png, .txt) found.")
    else:
        print(f"The {DATA_FOLDER} folder is empty.")
    return documents

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
