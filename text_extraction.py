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
        pdf_reader = PyPDF2.PdfFileReader(io.BytesIO(file_bytes))
        text = ""
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None