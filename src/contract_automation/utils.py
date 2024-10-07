import os
from typing import List
import asyncio
import aiofiles
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image

DATA_FOLDER = 'data'

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
        loader = PyPDFLoader(file_path)
        pages = await asyncio.to_thread(loader.load)
        return "\n".join(page.page_content for page in pages)
    elif file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        image = await asyncio.to_thread(Image.open, file_path)
        return ""  # Placeholder: Use another OCR solution if needed
    else:
        async with aiofiles.open(file_path, mode='r') as f:
            return await f.read()