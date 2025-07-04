from pypdf import PdfReader
import re
from typing import List, Dict

class DocumentProcessor:
    def __init__(self):
        self.chunks = []
        self.metadata = []

    def process_pdfs(self, pdf_files: List) -> List[Dict]:
        """Process uploaded PDFs and extract text chunks"""
        all_chunks = []

        for pdf_file in pdf_files:
            pdf_reader = PdfReader(pdf_file)

            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                cleaned_text = self.clean_text(text)
                chunks = self.chunk_text(cleaned_text, chunk_size=1000)

                for chunk in chunks:
                    all_chunks.append({
                        'content': chunk,
                        'source': pdf_file.name,
                        'page': page_num + 1,
                        'doc_type': self.classify_content(chunk)
                    })

        return all_chunks

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-\.\(\)\/\%]', '', text)
        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk.strip()) > 100:
                chunks.append(chunk)

        return chunks

    def classify_content(self, text: str) -> str:
        """Basic classification based on keywords"""
        text_lower = text.lower()
        if "operational" in text_lower or "operation" in text_lower:
            return "operational"
        elif "maintenance" in text_lower:
            return "maintenance"
        elif "troubleshooting" in text_lower or "error" in text_lower or "fault" in text_lower:
            return "troubleshooting"
        elif "regulatory" in text_lower or "regulation" in text_lower or "compliance" in text_lower:
            return "regulatory"
        else:
            return "other"