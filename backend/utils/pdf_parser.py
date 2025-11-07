"""
PDF Parser Utility
Extracts text from uploaded PDF files for policy comparison
"""

import PyPDF2
from typing import Optional
import io


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text content from a PDF file

    Args:
        pdf_file: File object or path to PDF file

    Returns:
        Extracted text content as string
    """
    text = ""

    try:
        # Handle file-like objects (from FastAPI UploadFile)
        if hasattr(pdf_file, 'read'):
            pdf_content = pdf_file.read()
            if isinstance(pdf_content, bytes):
                pdf_file_obj = io.BytesIO(pdf_content)
            else:
                pdf_file_obj = io.BytesIO(pdf_content.encode())
        else:
            # Handle file path
            pdf_file_obj = open(pdf_file, 'rb')

        # Extract text from PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Close file if we opened it
        if not hasattr(pdf_file, 'read'):
            pdf_file_obj.close()

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

    return text.strip()


def validate_pdf_file(filename: str) -> bool:
    """
    Validate if file is a PDF based on extension

    Args:
        filename: Name of the file

    Returns:
        True if valid PDF file, False otherwise
    """
    return filename.lower().endswith('.pdf')
