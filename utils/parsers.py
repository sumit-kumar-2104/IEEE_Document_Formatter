import os
import zipfile
import subprocess
from pathlib import Path
from .word_parser import parse_docx
from .pdf_parser import AcademicPDFParser
from pdf2docx import Converter



def parse_input_file(file_path):
    ext = Path(file_path).suffix.lower()
    
    if ext == '.pdf':
        # Use the improved PDF parser with hybrid approach
        parser = AcademicPDFParser()
        
        # First try direct PDF parsing
        pdf_result = parser.parse_pdf_direct(file_path)
        
        # Only attempt conversion if direct parsing was weak
        if not parser.is_better_result(pdf_result, {"sections": [], "abstract": ""}):
            docx_path = parser.convert_pdf_to_docx(file_path)
            if docx_path:
                try:
                    from word_parser import parse_docx  # Your existing DOCX parser
                    docx_result = parse_docx(docx_path)
                    os.remove(docx_path)  # Clean up temp file
                    
                    # Use whichever result is better
                    if parser.is_better_result(docx_result, pdf_result):
                        return docx_result
                except Exception as e:
                    print(f"DOCX parsing failed: {e}")
        
        return pdf_result
        
    elif ext == '.docx':
        from word_parser import parse_docx
        return parse_docx(file_path)
        
    elif ext == '.doc':
        converted_path = convert_to_docx(file_path)
        if converted_path:
            from word_parser import parse_docx
            return parse_docx(converted_path)
        return {"error": "DOC conversion failed"}
        
    elif ext == '.zip':
        return parse_zip(file_path)
        
    else:
        return {"error": "Unsupported file type"}


def has_useful_content(parsed):
    return (
        bool(parsed.get("abstract")) or
        bool(parsed.get("keywords")) or
        bool(parsed.get("sections"))
    )


def convert_pdf_to_docx(pdf_path):
    docx_path = str(Path(pdf_path).with_suffix('.docx'))
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        if os.path.exists(docx_path):
            return docx_path
    except Exception as e:
        print("PDF to DOCX conversion failed:", e)
    return None


def convert_to_docx(input_path):
    try:
        output_dir = str(Path(input_path).parent)
        result = subprocess.run([
            'soffice', '--headless', '--convert-to', 'docx', '--outdir', output_dir, input_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Decode safely to avoid UnicodeDecodeError on Windows
        stdout = result.stdout.decode('utf-8', errors='ignore')
        stderr = result.stderr.decode('utf-8', errors='ignore')
        print("LibreOffice stdout:", stdout)
        print("LibreOffice stderr:", stderr)

        converted_path = str(Path(input_path).with_suffix('.docx'))
        if os.path.exists(converted_path):
            return converted_path

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

# import os
# import zipfile
# import subprocess
# from pathlib import Path
# from .word_parser import parse_docx
# from .pdf_parser import parse_pdf
# from pdf2docx import Converter


# def parse_input_file(file_path):
#     ext = file_path.lower().split('.')[-1]
#     if ext == 'docx':
#         return parse_docx(file_path)

#     elif ext == 'doc':
#         converted_path = convert_to_docx(file_path)
#         if converted_path:
#             return parse_docx(converted_path)
#         else:
#             return {"error": "Failed to convert .doc to .docx"}

#     elif ext == 'pdf':
#         # Step 1: Try converting PDF to DOCX
#         converted_path = convert_pdf_to_docx(file_path)
#         if converted_path:
#             parsed = parse_docx(converted_path)

#             # Step 2: If parsed data is weak, fallback to PDF
#             if parsed and not has_useful_content(parsed):
#                 print("Fallback to parse_pdf due to weak docx content.")
#                 return parse_pdf(file_path)
#             return parsed
#         else:
#             # Step 3: Conversion failed, fallback to PDF parser
#             return parse_pdf(file_path)

#     elif ext == 'zip':
#         return parse_zip(file_path)

#     else:
#         return {"error": "Unsupported file type"}


# def has_useful_content(parsed):
#     return (
#         bool(parsed.get("abstract")) or
#         bool(parsed.get("keywords")) or
#         bool(parsed.get("sections"))
#     )


# def convert_pdf_to_docx(pdf_path):
#     docx_path = str(Path(pdf_path).with_suffix('.docx'))
#     try:
#         cv = Converter(pdf_path)
#         cv.convert(docx_path, start=0, end=None)
#         cv.close()
#         if os.path.exists(docx_path):
#             return docx_path
#     except Exception as e:
#         print("PDF to DOCX conversion failed:", e)
#     return None


# def convert_to_docx(input_path):
#     try:
#         output_dir = str(Path(input_path).parent)
#         result = subprocess.run([
#             'soffice', '--headless', '--convert-to', 'docx', '--outdir', output_dir, input_path
#         ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#         # Decode safely to avoid UnicodeDecodeError on Windows
#         stdout = result.stdout.decode('utf-8', errors='ignore')
#         stderr = result.stderr.decode('utf-8', errors='ignore')
#         print("LibreOffice stdout:", stdout)
#         print("LibreOffice stderr:", stderr)

#         converted_path = str(Path(input_path).with_suffix('.docx'))
#         if os.path.exists(converted_path):
#             return converted_path

#     except subprocess.CalledProcessError as e:
#         print("LibreOffice failed:", e)
#     except Exception as ex:
#         print("Conversion error:", ex)

#     return None



# def parse_zip(path):
#     import tempfile
#     parsed_results = []
#     with tempfile.TemporaryDirectory() as tmpdirname:
#         with zipfile.ZipFile(path, 'r') as zip_ref:
#             zip_ref.extractall(tmpdirname)
#             for name in zip_ref.namelist():
#                 full_path = os.path.join(tmpdirname, name)
#                 if os.path.isfile(full_path):
#                     parsed_results.append(parse_input_file(full_path))
#     return {"zip_contents": parsed_results}
