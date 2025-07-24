import docx
import re
import os
import shutil
from uuid import uuid4
from pathlib import Path
import hashlib

COMMON_SECTIONS = [
    "introduction", "literature review", "related work", "methodology",
    "methods", "results", "discussion", "experiments", "evaluation",
    "conclusion", "future work", "acknowledgment", "acknowledgement"
]
KEYWORD_HEADERS = ["keywords", "index terms"]
REFERENCE_HEADERS = ["references"]

def get_file_hash(file_path):
    """Generate a hash for the file to create consistent directory naming"""
    with open(file_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()[:8]
    return file_hash

def is_author_line(text):
    return bool(re.search(r'@\w+\.\w+', text)) or 'tcs' in text.lower() or 'university' in text.lower()

def is_possible_heading(text):
    text = text.strip()
    if not text or len(text.split()) > 15:
        return False
    if text.lower() in COMMON_SECTIONS:
        return True
    if re.match(r'^\d+(\.\d+)*[\.\)]?\s+[A-Z]', text):
        return True
    if re.match(r'^[A-Z][A-Za-z\s\-]{3,}$', text) and len(text.split()) <= 6:
        return True
    return False

def extract_heading_level(text):
    match = re.match(r'^(\d+(\.\d+)*)(\.|\))?\s+', text)
    return match.group(1) if match else None

def extract_images_from_docx(doc, image_dir, file_hash):
    """Enhanced image extraction with deduplication"""
    rels = doc.part.rels
    image_map = {}
    extracted_images = set()  # Track extracted images to prevent duplicates
    
    os.makedirs(image_dir, exist_ok=True)
    
    image_counter = 0
    for rel in rels.values():
        if "image" in rel.target_ref:
            try:
                # Generate hash of image content for deduplication
                image_content = rel.target_part.blob
                content_hash = hashlib.md5(image_content).hexdigest()
                
                # Skip if we've already extracted this exact image
                if content_hash in extracted_images:
                    print(f"[INFO] Skipping duplicate image: {content_hash[:8]}")
                    continue
                
                extracted_images.add(content_hash)
                image_counter += 1
                
                # Determine file extension
                image_extension = "png"  # Default
                try:
                    content_type = rel.target_part.content_type
                    if "jpeg" in content_type or "jpg" in content_type:
                        image_extension = "jpg"
                    elif "png" in content_type:
                        image_extension = "png"
                    elif "gif" in content_type:
                        image_extension = "gif"
                except:
                    pass
                
                # Generate consistent filename
                image_filename = f"{file_hash}_img_{image_counter:03d}.{image_extension}"
                image_path = os.path.join(image_dir, image_filename)
                
                # Extract image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_content)
                
                print(f"[INFO] Extracted unique image: {image_filename}")
                
                # Store relative path for web access
                web_path = f"/static/images/{os.path.basename(image_dir)}/{image_filename}"
                image_map[rel.rId] = web_path
                
            except Exception as e:
                print(f"[ERROR] Failed to extract image: {e}")
                continue
    
    return image_map

def find_blip_embeds(element):
    embeds = []
    for child in element.iter():
        if child.tag.endswith('blip'):
            embed = child.attrib.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
            if embed:
                embeds.append(embed)
    return embeds

def table_to_placeholder(table):
    """Convert table to inline placeholder and return table data"""
    table_id = str(uuid4())[:8]
    rows = []
    for row in table.rows:
        cells = [cell.text.strip() for cell in row.cells]
        rows.append(cells)
    return f"[TABLE: {table_id}]", table_id, rows

def create_image_metadata(image_path, caption="", image_index=0):
    """Create standardized image metadata"""
    if not os.path.exists(image_path.lstrip('/')):
        return None
    
    try:
        from PIL import Image
        full_path = image_path.lstrip('/')
        with Image.open(full_path) as img:
            width, height = img.size
            
        # Determine size category
        if width < 200 or height < 200:
            size_category = "small"
        elif width > 600 or height > 600:
            size_category = "large"
        else:
            size_category = "medium"
        
        return {
            "path": image_path,
            "filename": os.path.basename(image_path),
            "caption": caption or f"Figure {image_index + 1}",
            "size": size_category,
            "width": width,
            "height": height,
            "type": "image/png"
        }
    except Exception as e:
        print(f"[ERROR] Failed to create image metadata for {image_path}: {e}")
        return {
            "path": image_path,
            "filename": os.path.basename(image_path),
            "caption": caption or f"Figure {image_index + 1}",
            "size": "medium",
            "type": "image/png"
        }

def parse_docx(path):
    """Enhanced DOCX parser with fixed image deduplication"""
    if not os.path.exists(path):
        return {"error": "File not found"}
    
    # Generate consistent directory name based on file hash
    file_hash = get_file_hash(path)
    image_dir_name = f"doc_{file_hash}"
    image_dir = f'static/images/{image_dir_name}'
    
    # Ensure base static/images directory exists
    os.makedirs('static/images', exist_ok=True)
    
    try:
        doc = docx.Document(path)
    except Exception as e:
        return {"error": f"Failed to open DOCX file: {str(e)}"}
    
    # Extract images with deduplication
    image_map = extract_images_from_docx(doc, image_dir, file_hash)
    
    # Store table data with their IDs for inline processing
    table_data = {}

    result = {
        "title": "",
        "abstract": "",
        "keywords": "",
        "sections": [],
        "references": [],
        "images": [],
        "table_data": table_data,
        "template_type": "conference"  # Default template
    }

    current_section = None
    current_subsection = None
    in_references = False
    in_abstract = False
    title_found = False
    author_block_ended = False
    author_detected = False
    image_counter = 0
    processed_image_paths = set()  # Track processed images globally

    # Process all elements in document order (paragraphs and tables)
    for element in doc.element.body:
        if element.tag.endswith('p'):  # Paragraph
            para = docx.text.paragraph.Paragraph(element, doc)
            full_text = ""
            
            for run in para.runs:
                if run.text:
                    full_text += run.text

                # Fixed image extraction from run - prevent duplicates
                if run._element.xpath(".//pic:pic"):
                    embeds = find_blip_embeds(run._element)
                    for embed in embeds:
                        img_path = image_map.get(embed)
                        if img_path and img_path not in processed_image_paths:
                            # Only add image placeholder once
                            full_text += f' [IMAGE: {img_path}] '
                            processed_image_paths.add(img_path)
                            
                            # Create image metadata only once
                            img_metadata = create_image_metadata(img_path, "", image_counter)
                            if img_metadata:
                                result["images"].append(img_metadata)
                                image_counter += 1

            text = full_text.strip()
            if not text:
                continue

            # --- Title Detection ---
            if not title_found:
                if para.style.name.lower().startswith("title") or para.style.name.lower().startswith("heading 1"):
                    result["title"] = text
                    title_found = True
                    continue
                elif not re.match(r'(abstract|keywords?|index terms|references?)', text, re.IGNORECASE):
                    result["title"] = text
                    title_found = True
                    continue

            # --- Skip Author Lines ---
            if not author_block_ended:
                if is_author_line(text):
                    author_detected = True
                    continue
                if author_detected:
                    author_block_ended = True
                    continue
                continue

            # --- Abstract ---
            if re.match(r'^abstract\b', text, re.IGNORECASE):
                in_abstract = True
                result["abstract"] = ""
                continue

            if in_abstract:
                if re.match(r'^(keywords?|index terms|references?)\b', text, re.IGNORECASE) or is_possible_heading(text):
                    in_abstract = False
                else:
                    result["abstract"] += text + " "
                    continue

            # --- Keywords ---
            if any(text.lower().startswith(k) for k in KEYWORD_HEADERS):
                parts = re.split(r'[:\-]', text, 1)
                result["keywords"] = parts[1].strip() if len(parts) > 1 else text
                continue

            # --- References ---
            if any(text.lower().startswith(r) for r in REFERENCE_HEADERS):
                in_references = True
                if current_subsection and current_section:
                    current_section["subsections"].append(current_subsection)
                    current_subsection = None
                if current_section:
                    result["sections"].append(current_section)
                    current_section = None
                continue

            if in_references:
                result["references"].append(text)
                continue

            # --- Heading Detection ---
            level = extract_heading_level(text)
            if is_possible_heading(text) and not in_abstract and not in_references:
                if level and '.' in level:
                    if current_subsection:
                        current_section["subsections"].append(current_subsection)
                    current_subsection = {
                        "heading": text,
                        "content": "",
                        "images": []
                    }
                else:
                    if current_subsection and current_section:
                        current_section["subsections"].append(current_subsection)
                        current_subsection = None
                    if current_section:
                        result["sections"].append(current_section)
                    current_section = {
                        "heading": text,
                        "content": "",
                        "subsections": [],
                        "images": []
                    }
                continue

            # --- Content Appending ---
            if current_subsection:
                current_subsection["content"] += text + " "
            elif current_section:
                current_section["content"] += text + " "

        elif element.tag.endswith('tbl'):  # Table
            table = docx.table.Table(element, doc)
            table_placeholder, table_id, table_rows = table_to_placeholder(table)
            table_data[table_id] = table_rows
            
            # Add table placeholder to current content
            if current_subsection:
                current_subsection["content"] += table_placeholder + " "
            elif current_section:
                current_section["content"] += table_placeholder + " "

    # Finalize sections
    if current_subsection and current_section:
        current_section["subsections"].append(current_subsection)
    if current_section:
        result["sections"].append(current_section)

    # Fixed image distribution - prevent duplicates
    distribute_images_to_sections_fixed(result)

    print(f"[INFO] DOCX parsing completed. Found {len(result['sections'])} sections and {len(result['images'])} unique images")
    
    return result

def distribute_images_to_sections_fixed(result):
    """Fixed image distribution that prevents duplicates"""
    if not result["images"]:
        return
    
    # Initialize all sections with empty image arrays
    for section in result["sections"]:
        if "images" not in section:
            section["images"] = []
        for subsection in section.get("subsections", []):
            if "images" not in subsection:
                subsection["images"] = []
    
    # Track which images have been assigned to prevent duplicates
    assigned_images = set()
    
    # Check each section and subsection for image placeholders
    for section in result["sections"]:
        section_content = section.get("content", "")
        
        # Find images in section content
        for img in result["images"]:
            img_placeholder = f"[IMAGE: {img['path']}]"
            if img_placeholder in section_content and img['path'] not in assigned_images:
                # Create a copy of the image metadata to avoid reference issues
                img_copy = {
                    "path": img['path'],
                    "filename": img['filename'],
                    "caption": img['caption'],
                    "size": img['size'],
                    "width": img.get('width', 0),
                    "height": img.get('height', 0),
                    "type": img.get('type', 'image/png')
                }
                section["images"].append(img_copy)
                assigned_images.add(img['path'])
        
        # Check subsections
        for subsection in section.get("subsections", []):
            subsection_content = subsection.get("content", "")
            for img in result["images"]:
                img_placeholder = f"[IMAGE: {img['path']}]"
                if img_placeholder in subsection_content and img['path'] not in assigned_images:
                    # Create a copy of the image metadata
                    img_copy = {
                        "path": img['path'],
                        "filename": img['filename'],
                        "caption": img['caption'],
                        "size": img['size'],
                        "width": img.get('width', 0),
                        "height": img.get('height', 0),
                        "type": img.get('type', 'image/png')
                    }
                    subsection["images"].append(img_copy)
                    assigned_images.add(img['path'])
    
    # If no images were assigned to any section, put them in the first section (but only once)
    unassigned_images = [img for img in result["images"] if img['path'] not in assigned_images]
    if unassigned_images and result["sections"]:
        for img in unassigned_images:
            img_copy = {
                "path": img['path'],
                "filename": img['filename'],
                "caption": img['caption'],
                "size": img['size'],
                "width": img.get('width', 0),
                "height": img.get('height', 0),
                "type": img.get('type', 'image/png')
            }
            result["sections"][0]["images"].append(img_copy)
    
    print(f"[INFO] Distributed {len(assigned_images)} unique images to sections")
