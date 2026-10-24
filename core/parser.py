"""
Resume text parser supporting PDF, DOCX, DOC, and TXT files.
Features multi-engine extraction and zip-level DOCX fallback for zero failure.
"""

import os
import io
import re
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_file(file_path_or_bytes, filename=None):
    """
    Extracts text from a file path or file-like object / bytes.
    Automatically detects format by extension or file signature.
    """
    ext = ""
    is_path = isinstance(file_path_or_bytes, str) and os.path.exists(file_path_or_bytes)
    
    if is_path:
        filename = file_path_or_bytes
        ext = os.path.splitext(file_path_or_bytes)[1].lower()
    elif filename:
        ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        return extract_from_pdf(file_path_or_bytes, is_path)
    elif ext in ('.docx', '.doc'):
        return extract_from_docx(file_path_or_bytes, is_path)
    elif ext == '.txt':
        return extract_from_txt(file_path_or_bytes, is_path)
    else:
        # Try PDF, then DOCX, then TXT
        try:
            text = extract_from_pdf(file_path_or_bytes, is_path)
            if text and len(text.strip()) > 20:
                return text
        except Exception:
            pass

        try:
            text = extract_from_docx(file_path_or_bytes, is_path)
            if text and len(text.strip()) > 20:
                return text
        except Exception:
            pass

        return extract_from_txt(file_path_or_bytes, is_path)


def extract_from_pdf(file_source, is_path):
    """Extracts text from PDF using pdfplumber -> pypdf/PyPDF2 -> raw regex stream."""
    text_parts = []

    # 1. Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(file_source) as pdf:
            for page in pdf.pages:
                extract = page.extract_text()
                if extract:
                    text_parts.append(extract)
        if text_parts:
            return "\n".join(text_parts).strip()
    except Exception:
        pass

    # 2. Try pypdf or PyPDF2
    try:
        try:
            import pypdf
            reader_cls = pypdf.PdfReader
        except ImportError:
            import PyPDF2
            reader_cls = PyPDF2.PdfReader

        if is_path:
            reader = reader_cls(file_source)
        else:
            if isinstance(file_source, bytes):
                stream = io.BytesIO(file_source)
            elif hasattr(file_source, 'read'):
                file_source.seek(0)
                stream = io.BytesIO(file_source.read())
            else:
                stream = file_source
            reader = reader_cls(stream)

        for page in reader.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
        if text_parts:
            return "\n".join(text_parts).strip()
    except Exception:
        pass

    # 3. Fallback: Raw byte extraction for text strings in PDF
    try:
        if is_path:
            with open(file_source, 'rb') as f:
                content = f.read()
        elif isinstance(file_source, bytes):
            content = file_source
        elif hasattr(file_source, 'read'):
            file_source.seek(0)
            content = file_source.read()
        else:
            content = b""

        # Extract ASCII / UTF strings from stream objects
        raw_matches = re.findall(rb'\((.*?)\)Tj|\[(.*?)\]TJ', content)
        extracted = []
        for m1, m2 in raw_matches:
            target = m1 or m2
            cleaned = re.sub(rb'\\([()nrtfb\\])', rb'\1', target)
            try:
                extracted.append(cleaned.decode('utf-8', errors='ignore'))
            except Exception:
                pass
        if extracted:
            return " ".join(extracted).strip()
    except Exception:
        pass

    return ""


def extract_from_docx(file_source, is_path):
    """Extracts text from DOCX using python-docx or pure-Python XML zip parsing."""
    # 1. Try python-docx
    try:
        import docx
        if is_path:
            doc = docx.Document(file_source)
        else:
            if isinstance(file_source, bytes):
                stream = io.BytesIO(file_source)
            elif hasattr(file_source, 'read'):
                file_source.seek(0)
                stream = io.BytesIO(file_source.read())
            else:
                stream = file_source
            doc = docx.Document(stream)

        paragraphs = [p.text for p in doc.paragraphs if p.text]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        paragraphs.append(cell.text)
        return "\n".join(paragraphs).strip()
    except Exception:
        pass

    # 2. Fallback: Pure-Python ZIP extraction of word/document.xml
    try:
        if is_path:
            zf = zipfile.ZipFile(file_source)
        else:
            if isinstance(file_source, bytes):
                stream = io.BytesIO(file_source)
            elif hasattr(file_source, 'read'):
                file_source.seek(0)
                stream = io.BytesIO(file_source.read())
            else:
                stream = file_source
            zf = zipfile.ZipFile(stream)

        xml_content = zf.read('word/document.xml')
        tree = ET.fromstring(xml_content)
        # XML namespace for wordprocessingML
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text_elements = []
        for p in tree.iterfind('.//w:p', ns):
            p_text = "".join(node.text for node in p.iterfind('.//w:t', ns) if node.text)
            if p_text:
                text_elements.append(p_text)
        return "\n".join(text_elements).strip()
    except Exception:
        pass

    return ""


def extract_from_txt(file_source, is_path):
    """Reads TXT file with multiple encoding fallbacks."""
    if is_path:
        with open(file_source, 'rb') as f:
            raw = f.read()
    elif isinstance(file_source, bytes):
        raw = file_source
    elif hasattr(file_source, 'read'):
        file_source.seek(0)
        raw = file_source.read()
    else:
        return str(file_source)

    for enc in ('utf-8', 'utf-16', 'latin-1', 'cp1252', 'ascii'):
        try:
            return raw.decode(enc).strip()
        except UnicodeDecodeError:
            continue

    return raw.decode('utf-8', errors='ignore').strip()
