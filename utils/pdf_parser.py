import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import spacy
from pdf2docx import Converter
import uuid
from PIL import Image
import io
import base64
import json

# Load lightweight English model for NLP
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Warning: spaCy model 'en_core_web_sm' not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# Configuration
COMMON_SECTIONS = {
    "introduction", "related work", "literature review", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "conclusions", "future work", "acknowledgments", 
    "acknowledgements", "references", "bibliography", "appendix",
    "background", "approach", "implementation", "analysis", "findings"
}

SECTION_PATTERNS = [
    r'^(?P<num>\d+(\.\d+)*)\s*[\.\)]\s*(?P<title>.+)',  # 1.2. Section Title or 1.2) Section Title
    r'^(?P<num>[IVXLCDM]+)\.\s+(?P<title>.+)',  # Roman numerals
    r'^(?P<title>[A-Z][A-Za-z0-9\s\-:,]+)$',  # Title case alone on line
    r'^(?:APPENDIX|CHAPTER|SECTION)\s+(?P<num>[A-Z0-9]+)\s*[\.\-:]?\s*(?P<title>.*)$',  # Appendix A, Chapter 1, etc.
    r'^(?P<num>\d+)\s+(?P<title>[A-Z][A-Za-z0-9\s\-:,]+)$',  # 1 Introduction (without dot)
]

class AcademicPDFParser:
    def __init__(self):
        self.current_section = None
        self.in_references = False
        self.page_width = 0
        self.page_height = 0
        self.font_sizes = []
        self.common_font_size = 0

    def analyze_document_structure(self, doc):
        """Analyze document to understand structure patterns"""
        font_sizes = []
        
        for page in doc:
            self.page_width = page.rect.width
            self.page_height = page.rect.height
            
            # Get text with font information
            blocks = page.get_text("dict")
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            font_size = span.get("size", 0)
                            if font_size > 0:
                                font_sizes.append(font_size)
        
        # Determine common font size (body text)
        if font_sizes:
            font_sizes.sort()
            self.common_font_size = font_sizes[len(font_sizes) // 2]  # median
            self.font_sizes = list(set(font_sizes))
            self.font_sizes.sort(reverse=True)

    def is_header_footer(self, bbox, text: str) -> bool:
        """Detect headers and footers based on position and content"""
        x0, y0, x1, y1 = bbox
        
        # Position-based detection
        is_top_region = y0 < self.page_height * 0.1
        is_bottom_region = y1 > self.page_height * 0.9
        
        # Content-based detection
        is_short = len(text.split()) <= 5
        has_page_number = re.search(r'\b\d+\b', text)
        has_common_footer_words = any(word in text.lower() for word in 
                                     ['page', 'copyright', '©', 'proceedings', 'conference'])
        
        return (is_top_region or is_bottom_region) and (is_short or has_page_number or has_common_footer_words)

    def extract_images_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract images from PDF with metadata"""
        doc = fitz.open(pdf_path)
        images = []
        image_dir = f"static/images/{uuid.uuid4().hex[:8]}"
        os.makedirs(image_dir, exist_ok=True)
        
        for page_num, page in enumerate(doc):
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image data
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename
                    image_id = f"page_{page_num+1}_img_{img_index+1}"
                    image_filename = f"{image_id}.png"
                    image_path = os.path.join(image_dir, image_filename)
                    
                    # Convert and save as PNG
                    try:
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        pil_image = pil_image.convert("RGB")
                        pil_image.save(image_path, "PNG")
                        
                        # Get image position and size on page
                        img_rects = []
                        for block in page.get_drawings():
                            if hasattr(block, 'rect'):
                                img_rects.append(block.rect)
                        
                        # Determine size category based on image dimensions
                        width, height = pil_image.size
                        if width < 200 or height < 200:
                            size_category = "small"
                        elif width > 600 or height > 600:
                            size_category = "large"
                        else:
                            size_category = "medium"
                        
                        # Store image metadata
                        image_info = {
                            "path": f"/static/images/{os.path.basename(image_dir)}/{image_filename}",
                            "filename": image_filename,
                            "page": page_num + 1,
                            "size": size_category,
                            "width": width,
                            "height": height,
                            "caption": f"Figure from page {page_num + 1}",
                            "position": "center"
                        }
                        
                        images.append(image_info)
                        print(f"[INFO] Extracted image: {image_filename} ({width}x{height})")
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to process image {image_id}: {e}")
                        continue
                        
                except Exception as e:
                    print(f"[ERROR] Failed to extract image {img_index} from page {page_num}: {e}")
                    continue
        
        doc.close()
        return images

    def clean_text(self, text: str) -> str:
        """Advanced text cleaning with better hyphenation handling"""
        if not text:
            return ""
        
        # Fix hyphenated words across lines
        text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
        
        # Remove line breaks in the middle of sentences (but keep paragraph breaks)
        text = re.sub(r'(?<!\n)(?<!\.)(?<!:)\n(?!\n)(?![A-Z])(?!\d+\.)', ' ', text)
        
        # Clean multiple whitespace
        text = re.sub(r'[ \t]{2,}', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove PDF artifacts and special characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # Fix common OCR issues
        text = re.sub(r'\bl\b(?=\w)', 'I', text)  # lone 'l' should be 'I'
        text = re.sub(r'\b0(?=[A-Za-z])', 'O', text)  # '0' before letters should be 'O'
        
        return text.strip()

    def extract_text_with_structure(self, pdf_path: str) -> Tuple[str, List[Dict]]:
        """Enhanced text extraction preserving structure and font information"""
        doc = fitz.open(pdf_path)
        self.analyze_document_structure(doc)
        
        structured_blocks = []
        all_text = []
        
        for page_num, page in enumerate(doc):
            # Get text blocks with detailed formatting
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                    
                block_text = ""
                block_fonts = []
                block_bbox = block.get("bbox", [0, 0, 0, 0])
                
                # Skip headers/footers
                if self.is_header_footer(block_bbox, ""):
                    continue
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line.get("spans", []):
                        span_text = span.get("text", "").strip()
                        if span_text:
                            line_text += span_text + " "
                            block_fonts.append({
                                "size": span.get("size", 0),
                                "flags": span.get("flags", 0),
                                "font": span.get("font", "")
                            })
                    
                    if line_text.strip():
                        block_text += line_text.strip() + "\n"
                
                if block_text.strip():
                    # Determine if this is likely a heading based on font analysis
                    avg_font_size = sum(f["size"] for f in block_fonts) / len(block_fonts) if block_fonts else 0
                    is_bold = any(f["flags"] & 2**4 for f in block_fonts)  # Bold flag
                    is_larger = avg_font_size > self.common_font_size * 1.1
                    
                    structured_block = {
                        "text": self.clean_text(block_text),
                        "page": page_num + 1,
                        "bbox": block_bbox,
                        "font_size": avg_font_size,
                        "is_bold": is_bold,
                        "is_larger": is_larger,
                        "likely_heading": (is_larger or is_bold) and len(block_text.split()) <= 15
                    }
                    
                    structured_blocks.append(structured_block)
                    all_text.append(block_text)
        
        doc.close()
        return "\n\n".join(all_text), structured_blocks

    def is_section_header(self, text: str, font_info: Dict = None) -> Tuple[bool, Optional[str]]:
        """Enhanced section header detection with font information"""
        if not text or len(text.split()) > 20:
            return False, None
        
        text = text.strip()
        text_lower = text.lower()
        
        # Font-based detection (if available)
        if font_info and (font_info.get("is_larger") or font_info.get("is_bold")):
            if len(text.split()) <= 10:
                # Check against common sections
                for section in COMMON_SECTIONS:
                    if section in text_lower:
                        return True, text
        
        # Pattern-based detection
        for pattern in SECTION_PATTERNS:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return True, text
        
        # Check against common section names
        if any(section == text_lower.strip('.').strip(':') for section in COMMON_SECTIONS):
            return True, text
        
        # NLP-based check (if spaCy is available)
        if nlp and len(text.split()) <= 8:
            doc = nlp(text)
            # Look for patterns common in academic section headings
            has_important_nouns = any(
                token.pos_ in ["NOUN", "PROPN"] and token.text.lower() in COMMON_SECTIONS
                for token in doc
            )
            if has_important_nouns:
                return True, text
        
        return False, None

    def extract_title_and_authors(self, structured_blocks: List[Dict]) -> Tuple[str, List[str]]:
        """Extract title and authors from the beginning of the document"""
        title = ""
        authors = []
        
        # Look at first few blocks for title
        for i, block in enumerate(structured_blocks[:5]):
            text = block["text"].strip()
            if not text:
                continue
                
            # Title is usually the largest/bold text at the beginning
            if not title and (block.get("is_larger") or block.get("is_bold")):
                # Avoid abstracts, keywords as titles
                if not re.match(r'^(abstract|keywords?|index terms)', text, re.I):
                    title = text
                    continue
            
            # Authors often contain email patterns or affiliations
            if re.search(r'@\w+\.\w+', text) or any(word in text.lower() for word in 
                        ['university', 'institute', 'department', 'college', 'lab']):
                authors.append(text)
                continue
            
            # Stop looking after we find a clear section header
            is_header, _ = self.is_section_header(text, block)
            if is_header:
                break
        
        return title, authors

    def extract_abstract_and_keywords(self, text: str) -> Tuple[str, str]:
        """Extract abstract and keywords with improved regex patterns"""
        abstract = ""
        keywords = ""
        
        # Abstract patterns
        abstract_patterns = [
            r'\babstract\b[:\s\-–]*\n*(.*?)(?=\n\s*(?:keywords?|index terms|1\.?\s+introduction|\d+\.?\s+\w+))',
            r'\babstract\b[:\s\-–]*\n*(.*?)(?=\n{2,})',
            r'\babstract\b[:\s\-–]*(.*?)(?=keywords?|index terms|introduction)'
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                abstract = re.sub(r'\n+', ' ', match.group(1)).strip()
                if len(abstract) > 50:  # Ensure it's substantial
                    break
        
        # Keywords patterns
        keyword_patterns = [
            r'\b(?:keywords?|index terms)\b[:\s\-–]*\n*([^\n]+(?:\n[^\n]+)*?)(?=\n\s*(?:1\.?\s+introduction|\d+\.?\s+\w+|\n{2,}))',
            r'\b(?:keywords?|index terms)\b[:\s\-–]*([^\n]+)',
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                keywords = match.group(1).strip()
                # Clean up keywords
                keywords = re.sub(r'\n+', ', ', keywords)
                keywords = re.sub(r'[;,]\s*', ', ', keywords)
                break
        
        return abstract, keywords

    def parse_pdf_direct(self, pdf_path: str) -> Dict:
        """Enhanced direct PDF parsing with structure awareness"""
        full_text, structured_blocks = self.extract_text_with_structure(pdf_path)
        images = self.extract_images_from_pdf(pdf_path)
        
        # Extract title and authors
        title, authors = self.extract_title_and_authors(structured_blocks)
        
        # Extract abstract and keywords
        abstract, keywords = self.extract_abstract_and_keywords(full_text)
        
        result = {
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "authors": authors,
            "sections": [],
            "references": [],
            "images": images,
            "table_data": {}  # For compatibility with existing code
        }
        
        # Parse sections using structured blocks
        current_section = None
        current_subsection = None
        in_references = False
        
        for block in structured_blocks:
            text = block["text"]
            if not text:
                continue
            
            # Check for references section
            if re.match(r'^\s*references?\s*$', text, re.IGNORECASE):
                in_references = True
                if current_subsection and current_section:
                    current_section["subsections"].append(current_subsection)
                if current_section:
                    result["sections"].append(current_section)
                current_section = None
                current_subsection = None
                continue
            
            if in_references:
                # Parse reference entries
                ref_lines = [line.strip() for line in text.split('\n') if line.strip()]
                result["references"].extend(ref_lines)
                continue
            
            # Check if this is a section header
            is_header, header_text = self.is_section_header(text, block)
            
            if is_header:
                # Determine if it's a main section or subsection
                has_number = re.match(r'^\d+(\.\d+)*', text)
                is_subsection = has_number and '.' in has_number.group(1)
                
                if is_subsection and current_section:
                    # This is a subsection
                    if current_subsection:
                        current_section["subsections"].append(current_subsection)
                    current_subsection = {
                        "heading": header_text,
                        "content": "",
                        "images": []
                    }
                else:
                    # This is a main section
                    if current_subsection and current_section:
                        current_section["subsections"].append(current_subsection)
                    if current_section:
                        result["sections"].append(current_section)
                    
                    current_section = {
                        "heading": header_text,
                        "content": "",
                        "subsections": [],
                        "images": []
                    }
                    current_subsection = None
                continue
            
            # Add content to current section/subsection
            if current_subsection:
                current_subsection["content"] += text + " "
            elif current_section:
                current_section["content"] += text + " "
        
        # Add final section
        if current_subsection and current_section:
            current_section["subsections"].append(current_subsection)
        if current_section:
            result["sections"].append(current_section)
        
        # Distribute images to sections based on page numbers
        self.distribute_images_to_sections(result, images)
        
        # Clean up section content
        for section in result["sections"]:
            section["content"] = self.clean_text(section["content"])
            for subsection in section.get("subsections", []):
                subsection["content"] = self.clean_text(subsection["content"])
        
        return result

    def distribute_images_to_sections(self, result: Dict, images: List[Dict]):
        """Distribute images to appropriate sections based on page proximity"""
        if not images:
            return
        
        for image in images:
            page_num = image["page"]
            best_section = None
            
            # Find the section that's most likely to contain this image
            for section in result["sections"]:
                if not best_section:
                    best_section = section
                # More sophisticated logic could be added here based on content analysis
            
            if best_section:
                best_section["images"].append(image)

    def convert_pdf_to_docx(self, pdf_path: str) -> Optional[str]:
        """Robust PDF to DOCX conversion with better error handling"""
        docx_path = str(Path(pdf_path).with_suffix('.docx'))
        
        try:
            # Check if input file is valid
            if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
                return None
            
            cv = Converter(pdf_path)
            cv.convert(
                docx_path,
                start=0,
                end=None,
                keep_blank_lines=False,
                debug=False
            )
            cv.close()
            
            # Verify conversion success
            if os.path.exists(docx_path) and os.path.getsize(docx_path) > 1024:
                return docx_path
            else:
                # Clean up failed conversion
                if os.path.exists(docx_path):
                    os.remove(docx_path)
                return None
                
        except Exception as e:
            print(f"[ERROR] PDF to DOCX conversion failed: {e}")
            # Clean up on failure
            if os.path.exists(docx_path):
                try:
                    os.remove(docx_path)
                except:
                    pass
            return None

    def parse_pdf(self, pdf_path: str) -> Dict:
        """Main parsing method with hybrid approach and better fallbacks"""
        print(f"[INFO] Starting PDF parsing: {pdf_path}")
        
        # Validate input
        if not os.path.exists(pdf_path):
            return {"error": "File not found"}
        
        if os.path.getsize(pdf_path) == 0:
            return {"error": "Empty file"}
        
        # First try direct PDF parsing (usually more reliable)
        try:
            print("[INFO] Attempting direct PDF parsing...")
            pdf_result = self.parse_pdf_direct(pdf_path)
            
            # Basic validation of results
            if pdf_result.get("title") or pdf_result.get("sections"):
                print(f"[SUCCESS] Direct PDF parsing successful. Found {len(pdf_result.get('sections', []))} sections")
                return pdf_result
                
        except Exception as e:
            print(f"[ERROR] Direct PDF parsing failed: {e}")
        
        # Fallback to DOCX conversion method
        try:
            print("[INFO] Attempting PDF to DOCX conversion method...")
            docx_path = self.convert_pdf_to_docx(pdf_path)
            
            if docx_path:
                try:
                    # Import your DOCX parser
                    from .word_parser import parse_docx
                    docx_result = parse_docx(docx_path)
                    
                    # Add image extraction from original PDF
                    images = self.extract_images_from_pdf(pdf_path)
                    docx_result["images"] = images
                    
                    # Clean up temporary file
                    os.remove(docx_path)
                    
                    print(f"[SUCCESS] DOCX conversion method successful. Found {len(docx_result.get('sections', []))} sections")
                    return docx_result
                    
                except Exception as e:
                    print(f"[ERROR] DOCX parsing failed: {e}")
                    if os.path.exists(docx_path):
                        os.remove(docx_path)
                        
        except Exception as e:
            print(f"[ERROR] DOCX conversion method failed: {e}")
        
        # Final fallback: basic text extraction
        try:
            print("[INFO] Using basic text extraction fallback...")
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            return {
                "title": "Extracted Document",
                "abstract": "",
                "keywords": "",
                "sections": [{
                    "heading": "Content",
                    "content": self.clean_text(text),
                    "subsections": [],
                    "images": []
                }],
                "references": [],
                "images": [],
                "table_data": {}
            }
            
        except Exception as e:
            print(f"[ERROR] All parsing methods failed: {e}")
            return {"error": f"Failed to parse PDF: {str(e)}"}

    def is_better_result(self, new_result: Dict, old_result: Dict) -> bool:
        """Enhanced comparison logic for parsing results"""
        if "error" in new_result:
            return False
        if "error" in old_result:
            return True
        
        # Compare number of sections
        new_sections = len(new_result.get("sections", []))
        old_sections = len(old_result.get("sections", []))
        
        # Compare content richness
        new_abstract = bool(new_result.get("abstract", "").strip())
        old_abstract = bool(old_result.get("abstract", "").strip())
        
        new_title = bool(new_result.get("title", "").strip())
        old_title = bool(old_result.get("title", "").strip())
        
        new_keywords = bool(new_result.get("keywords", "").strip())
        old_keywords = bool(old_result.get("keywords", "").strip())
        
        # Scoring system
        new_score = new_sections + (2 if new_abstract else 0) + (1 if new_title else 0) + (1 if new_keywords else 0)
        old_score = old_sections + (2 if old_abstract else 0) + (1 if old_title else 0) + (1 if old_keywords else 0)
        
        return new_score > old_score


def parse_pdf(file_path: str) -> Dict:
    """Main entry point for PDF parsing"""
    parser = AcademicPDFParser()
    return parser.parse_pdf(file_path)


# # Usage example
# if __name__ == "__main__":
#     parser = AcademicPDFParser()
#     result = parser.parse_pdf("your_paper.pdf")
    
#     # Pretty print results
#     import json
#     print(json.dumps({k: v for k, v in result.items() if k != "images"}, indent=2))
#     print(f"Found {len(result.get('images', []))} images")
