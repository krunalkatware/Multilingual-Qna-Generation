import os
import re
from pypdf import PdfReader
from docx import Document


def extract_text_from_pdf(file):
    try:
        reader = PdfReader(file)
        pages_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                pages_text.append(text.strip())

        if not pages_text:
            raise ValueError("No readable text found in the PDF.")

        return "\n\n".join(pages_text)
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to read PDF: {str(e)}")


def extract_text_from_docx(file):
    try:
        doc = Document(file)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        if not paragraphs:
            raise ValueError("No readable text found in the DOCX file.")

        return "\n\n".join(paragraphs)
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to read DOCX: {str(e)}")


def extract_text_from_txt(file):
    try:
        if hasattr(file, "read"):
            content = file.read()
            if isinstance(content, bytes):
                text = content.decode("utf-8", errors="replace")
            else:
                text = str(content)
        else:
            with open(file, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()

        if not text.strip():
            raise ValueError("The text file is empty.")

        return text
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise ValueError(f"Failed to read TXT: {str(e)}")


def clean_text(text):
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(file, filename=None):
    if filename:
        name = filename
    elif hasattr(file, "name"):
        name = file.name
    elif isinstance(file, str):
        name = file
    else:
        name = ""

    ext = os.path.splitext(name)[1].lower()

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file)
    elif ext == ".txt":
        raw_text = extract_text_from_txt(file)
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please upload a .pdf, .docx, or .txt file.")

    cleaned = clean_text(raw_text)
    if not cleaned or len(cleaned) < 10:
        raise ValueError("The document does not contain enough meaningful text.")

    return cleaned
