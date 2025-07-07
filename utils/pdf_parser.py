# import fitz  # PyMuPDF
# import re

# COMMON_SECTIONS = {
#     "introduction", "related work", "literature review", "methodology",
#     "methods", "results", "discussion", "experiments", "evaluation",
#     "conclusion", "future work", "acknowledgment", "acknowledgement"
# }

# EMAIL_REGEX = re.compile(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b')
# AFFILIATION_KEYWORDS = [
#     "university", "institute", "department", "college", "school",
#     "research", "tcs", "technologies", "engineering"
# ]

# def is_possible_section_heading(text):
#     text = text.strip()
#     if not text or len(text.split()) > 15:
#         return False
#     if text.lower() in COMMON_SECTIONS:
#         return True
#     return bool(re.match(r'^([IVXLC]+\.|\d+[\.\)])?\s*[A-Z][A-Za-z0-9\s\-:,]{1,80}$', text))

# def is_affiliation_line(text):
#     text = text.lower()
#     return any(kw in text for kw in AFFILIATION_KEYWORDS) or EMAIL_REGEX.search(text)

# def parse_pdf(file_path):
#     try:
#         doc = fitz.open(file_path)
#     except Exception as e:
#         print("PDF open failed:", e)
#         return {"error": "Could not open PDF"}

#     raw_text = "\n".join([page.get_text("text") for page in doc])
#     raw_text = re.sub(r'\s+\n', '\n', raw_text)
#     lines = [line.strip() for line in raw_text.split('\n') if line.strip()]

#     result = {
#         "title": "",
#         "abstract": "",
#         "keywords": "",
#         "sections": [],
#         "references": []
#     }

#     current_section = None
#     in_references = False
#     title_found = False
#     author_detected = False
#     author_block_skipped = False

#     i = 0
#     while i < len(lines):
#         line = lines[i].strip()
#         lower = line.lower()

#         # Skip author lines (affiliations/emails)
#         if not author_block_skipped:
#             if is_affiliation_line(line):
#                 author_detected = True
#                 i += 1
#                 continue
#             if author_detected:
#                 author_block_skipped = True
#                 i += 1
#                 continue
#             i += 1
#             continue

#         # --- Title ---
#         if not title_found:
#             result["title"] = line
#             title_found = True
#             i += 1
#             continue

#         # --- Abstract ---
#         if re.match(r'^abstract\b', lower):
#             abstract = []

#             inline_match = re.match(r'^abstract\b[:\-\—]?\s*(.+)', line, flags=re.I)
#             if inline_match:
#                 abstract.append(inline_match.group(1).strip())

#             i += 1
#             while i < len(lines):
#                 next_line = lines[i].strip()
#                 lower_next = next_line.lower()

#                 if re.match(r'^(keywords?|index terms|references?)\b', lower_next) or is_affiliation_line(next_line):
#                     break
#                 abstract.append(next_line)
#                 i += 1

#             result["abstract"] = " ".join(abstract).strip()
#             continue

#         # --- Keywords ---
#         if re.match(r'^(keywords|index terms)\b[:\-\—]?', lower):
#             keyword_line = re.sub(r'^(keywords|index terms)[:\-\—]?', '', line, flags=re.I).strip()
#             keyword_parts = [keyword_line]
#             i += 1
#             while i < len(lines):
#                 next_line = lines[i].strip()
#                 if is_possible_section_heading(next_line) or next_line.lower().startswith("introduction"):
#                     break
#                 keyword_parts.append(next_line)
#                 i += 1
#             result["keywords"] = " ".join(keyword_parts).strip()
#             continue

#         # --- References ---
#         if re.match(r'^references\b', lower):
#             in_references = True
#             if current_section:
#                 result["sections"].append(current_section)
#                 current_section = None
#             i += 1
#             continue

#         if in_references:
#             result["references"].append(line)
#             i += 1
#             continue

#         # --- Section Heading ---
#         if is_possible_section_heading(line):
#             if current_section:
#                 result["sections"].append(current_section)
#             current_section = {
#                 "heading": line,
#                 "content": "",
#                 "subsections": []
#             }
#         elif current_section:
#             current_section["content"] += line + " "

#         i += 1

#     # Finalize last section
#     if current_section:
#         result["sections"].append(current_section)

#     # Safety fallback
#     if not result["title"] and not result["abstract"] and not result["sections"]:
#         return {"error": "Unable to parse PDF content"}

#     return result


import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional
import spacy
from pdf2docx import Converter

# Load lightweight English model for NLP
nlp = spacy.load("en_core_web_sm")

# Configuration
COMMON_SECTIONS = {
    "introduction", "related work", "literature review", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "future work", "acknowledgments", "references"
}

SECTION_PATTERNS = [
    r'^(?P<num>\d+(\.\d+)*)\s+(?P<title>.+)',  # 1.2 Section Title
    r'^(?P<title>[A-Z][A-Za-z0-9\s\-:]+)$',  # Title case alone on line
    r'^(?:APPENDIX|CHAPTER|SECTION)\s+.+$',  # Appendix A, Chapter 1, etc.
    r'^[IVXLCDM]+\.\s+.+$',  # Roman numerals
]

class AcademicPDFParser:
    def __init__(self):
        self.current_section = None
        self.in_references = False

    def clean_text(self, text: str) -> str:
        """Remove unwanted artifacts from extracted text"""
        # Remove line breaks in the middle of sentences
        text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
        # Remove multiple spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)
        # Remove special characters often from PDF artifacts
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        return text.strip()

    def extract_text_with_structure(self, pdf_path: str) -> str:
        """Improved text extraction that preserves logical structure"""
        doc = fitz.open(pdf_path)
        clean_blocks = []
        
        for page in doc:
            blocks = page.get_text("blocks", sort=True)
            for block in blocks:
                text = block[4].strip()
                if not text or len(text.split()) < 2:
                    continue
                    
                # Skip headers/footers based on position
                if (block[1] < 50 or block[3] > page.rect.height - 50) and len(text.split()) < 5:
                    continue
                    
                clean_blocks.append(self.clean_text(text))
        
        return "\n\n".join(clean_blocks)

    def is_section_header(self, text: str) -> bool:
        """Improved section header detection"""
        text_lower = text.lower()
        
        # Check against common section names
        if any(section in text_lower for section in COMMON_SECTIONS):
            return True
            
        # Check structural patterns
        if any(re.fullmatch(pattern, text, flags=re.IGNORECASE) for pattern in SECTION_PATTERNS):
            return True
            
        # NLP-based check for short, important phrases
        if len(text.split()) <= 6:
            doc = nlp(text)
            # Check for proper nouns or nouns that might be section headings
            if any(token.pos_ in ["PROPN", "NOUN"] and token.text.istitle() for token in doc):
                return True
                
        return False

    def parse_pdf_direct(self, pdf_path: str) -> Dict:
        """Parse PDF directly with improved structure detection"""
        full_text = self.extract_text_with_structure(pdf_path)
        lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        
        result = {
            "title": "",
            "abstract": "",
            "keywords": "",
            "sections": [],
            "references": []
        }
        
        self.current_section = None
        self.in_references = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect title (first significant line)
            if not result["title"] and len(line.split()) <= 15 and line[0].isupper():
                result["title"] = line
                i += 1
                continue
                
            # Detect abstract
            if not result["abstract"] and re.match(r'^abstract\b', line, re.I):
                abstract_lines = []
                i += 1
                while i < len(lines) and not self.is_section_header(lines[i]):
                    abstract_lines.append(lines[i])
                    i += 1
                result["abstract"] = " ".join(abstract_lines)
                continue
                
            # Detect references section
            if re.match(r'^references\b', line, re.I):
                self.in_references = True
                if self.current_section:
                    result["sections"].append(self.current_section)
                    self.current_section = None
                i += 1
                continue
                
            # Handle references content
            if self.in_references:
                result["references"].append(line)
                i += 1
                continue
                
            # Detect section headers
            if self.is_section_header(line):
                if self.current_section:
                    result["sections"].append(self.current_section)
                self.current_section = {
                    "heading": line,
                    "content": []
                }
                i += 1
                continue
                
            # Add content to current section
            if self.current_section:
                self.current_section["content"].append(line)
                
            i += 1
        
        # Add the last section if exists
        if self.current_section:
            result["sections"].append(self.current_section)
            
        # Clean section content by joining lines
        for section in result["sections"]:
            section["content"] = " ".join(section["content"])
            
        return result

    def convert_pdf_to_docx(self, pdf_path: str) -> Optional[str]:
        """Robust PDF to DOCX conversion with cleanup"""
        docx_path = str(Path(pdf_path).with_suffix('.docx'))
        
        try:
            cv = Converter(pdf_path)
            cv.convert(
                docx_path,
                start=0,
                end=None,
                keep_blank_lines=False,
                debug=False
            )
            cv.close()
            
            if os.path.exists(docx_path) and os.path.getsize(docx_path) > 1024:
                return docx_path
        except Exception as e:
            print(f"PDF to DOCX conversion failed: {e}")
            
        return None

    def parse_pdf(self, pdf_path: str) -> Dict:
        """Hybrid PDF parsing with fallback to direct parsing"""
        # First try direct PDF parsing
        pdf_result = self.parse_pdf_direct(pdf_path)
        
        # Then try DOCX conversion path
        docx_path = self.convert_pdf_to_docx(pdf_path)
        if docx_path:
            try:
                from .word_parser import parse_docx  # Import your DOCX parser
                docx_result = parse_docx(docx_path)
                os.remove(docx_path)  # Clean up
                
                # Validate and compare results
                if self.is_better_result(docx_result, pdf_result):
                    return docx_result
            except Exception as e:
                print(f"DOCX parsing failed: {e}")
                
        return pdf_result

    def is_better_result(self, new_result: Dict, old_result: Dict) -> bool:
        """Determine which parsing result is better"""
        # Compare number of sections
        new_sections = len(new_result.get("sections", []))
        old_sections = len(old_result.get("sections", []))
        
        # Compare abstract presence
        new_abstract = bool(new_result.get("abstract"))
        old_abstract = bool(old_result.get("abstract"))
        
        return (new_sections > old_sections) or (new_abstract and not old_abstract)

# Usage example
if __name__ == "__main__":
    parser = AcademicPDFParser()
    result = parser.parse_pdf("your_paper.pdf")
    print(result)


    






    



#def parse_pdf(file_path):
#     doc = fitz.open(file_path)

#     # Step 1: Clean and normalize text
#     full_text = "\n".join([page.get_text("text") for page in doc])
#     text = re.sub(r'\s+\n', '\n', full_text)          # clean space before newline
#     text = re.sub(r'\n{2,}', '\n\n', text).strip()    # normalize paragraph breaks

#     result = {
#         "title": "",
#         "abstract": "",
#         "keywords": "",
#         "sections": [],
#         "references": []
#     }

#     # Step 2: Split into lines and basic title
#     lines = [line.strip() for line in text.splitlines() if line.strip()]
#     if lines:
#         result["title"] = lines[0]

#     # Step 3: Extract Abstract
#     abstract_match = re.search(
#         r'\babstract\b[:\s\-–]*([\s\S]*?)(?=\n{2,}|\bkeywords\b|\bindex terms\b|\breferences\b|\b1[\.\s])',
#         text, re.IGNORECASE
#     )
#     if abstract_match:
#         result["abstract"] = re.sub(r'\n+', ' ', abstract_match.group(1)).strip()

#     # Step 4: Extract Keywords
#     keyword_match = re.search(r'\b(keywords|index terms)\b[:\s\-–]*([^\n]+)', text, re.IGNORECASE)
#     if keyword_match:
#         result["keywords"] = keyword_match.group(2).strip()

#     # Step 5: Extract References
#     ref_match = re.search(r'\breferences\b', text, re.IGNORECASE)
#     if ref_match:
#         content_text = text[:ref_match.start()]
#         ref_text = text[ref_match.end():]
#         # Matches: [1] something, 1. something, 1) something
#         result["references"] = re.findall(
#             r'(?:\[\d+\]|\n\d{1,2}[.)])\s+(.*?)(?=(?:\[\d+\]|\n\d{1,2}[.)])|\Z)',
#             ref_text, re.DOTALL
#         )
#     else:
#         content_text = text

#     # Step 6: Detect Sections
#     section_lines = content_text.splitlines()
#     sections = []
#     section_indices = []

#     for i, line in enumerate(section_lines):
#         clean_line = line.strip()
#         if not clean_line:
#             continue
#         # If looks like: "1. Introduction" OR "Conclusion" OR "Related Work" etc.
#         if (
#             re.match(r'^(\d+\s*[\.\)]|[IVXLC]+\.)?\s*[A-Z][^\n]{1,80}$', clean_line)
#             and len(clean_line.split()) <= 10
#         ):
#             section_indices.append((i, clean_line))

#     for idx, (line_num, heading) in enumerate(section_indices):
#         start = line_num + 1
#         end = section_indices[idx + 1][0] if idx + 1 < len(section_indices) else len(section_lines)
#         content_lines = section_lines[start:end]
#         body = " ".join(l.strip() for l in content_lines if l.strip())
#         sections.append({
#             "heading": heading,
#             "content": body,
#             "subsections": []  # can be filled later if needed
#         })

#     result["sections"] = sections
#     return result
