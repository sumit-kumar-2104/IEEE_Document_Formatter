import os
import zipfile
import subprocess
from pathlib import Path
from pdf2docx import Converter
from .pdf_parser import AcademicPDFParser
from .word_parser import parse_docx

def parse_input_file(file_path):
    ext = Path(file_path).suffix.lower()

    if ext == '.pdf':
        parser = AcademicPDFParser()
        pdf_result = parser.parse_pdf_direct(file_path)

        if not parser.is_better_result(pdf_result, {"sections": [], "abstract": ""}):
            docx_path = convert_pdf_to_docx(file_path)
            if docx_path:
                try:
                    docx_result = parse_docx(docx_path)
                    os.remove(docx_path)
                    return docx_result if parser.is_better_result(docx_result, pdf_result) else pdf_result
                except Exception as e:
                    print(f"DOCX parsing failed: {e}")
        return pdf_result

    elif ext == '.docx':
        return parse_docx(file_path)

    elif ext == '.doc':
        converted_path = convert_to_docx(file_path)
        if converted_path:
            return parse_docx(converted_path)
        return {"error": "DOC conversion failed"}

    elif ext == '.zip':
        return parse_zip(file_path)

    else:
        return {"error": "Unsupported file type"}


def convert_pdf_to_docx(pdf_path):
    docx_path = str(Path(pdf_path).with_suffix('.docx'))
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return docx_path if os.path.exists(docx_path) else None
    except Exception as e:
        print("PDF to DOCX conversion failed:", e)
        return None


def convert_to_docx(input_path):
    try:
        output_dir = str(Path(input_path).parent)
        subprocess.run([
            'soffice', '--headless', '--convert-to', 'docx', '--outdir', output_dir, input_path
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        converted_path = str(Path(input_path).with_suffix('.docx'))
        return converted_path if os.path.exists(converted_path) else None
    except subprocess.CalledProcessError as e:
        print("LibreOffice failed:", e)
    except Exception as ex:
        print("Conversion error:", ex)
    return None


def parse_zip(path):
    import tempfile
    parsed_results = []
    with tempfile.TemporaryDirectory() as tmpdirname:
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
            for name in zip_ref.namelist():
                full_path = os.path.join(tmpdirname, name)
                if os.path.isfile(full_path):
                    parsed_results.append(parse_input_file(full_path))
    return {"zip_contents": parsed_results}
