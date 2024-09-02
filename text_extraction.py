import docx
import PyPDF2
import io
import streamlit as st

def extract_text_from_docx(file_bytes):
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return None

def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page_num in range(len(pdf_reader.pages)):  # Use len(pdf_reader.pages)
            page = pdf_reader.pages[page_num]         # Access pages using []
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None