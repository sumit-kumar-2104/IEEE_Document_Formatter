from jinja2 import Environment, BaseLoader
import re
import os
import shutil
from PIL import Image
import base64
import uuid
import unicodedata

# IEEE Conference Template
IEEE_CONFERENCE_TEMPLATE = r"""
\documentclass[conference]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{caption}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage[export]{adjustbox}
\usepackage{cite}

\title{<< title >>}
\author{
{% if authors %}
{% for author in authors %}
\IEEEauthorblockN{<< author.name >>}
\IEEEauthorblockA{<< author.affiliation >>\\
<< author.email >>}
{% if not loop.last %}\and{% endif %}
{% endfor %}
{% endif %}
}

\begin{document}
\maketitle

{% if abstract %}
\begin{abstract}
<< abstract >>
\end{abstract}
{% endif %}

{% if keywords %}
\begin{IEEEkeywords}
<< keywords >>
\end{IEEEkeywords}
{% endif %}

{% for section in sections %}
\section{<< section.heading >>}
<< section.content >>

{% for sub in section.subsections %}
\subsection{<< sub.heading >>}
<< sub.content >>
{% endfor %}
{% endfor %}

{% if references %}
\begin{thebibliography}{99}
{% for ref in references %}
\bibitem{ref<< loop.index >>} << ref >>
{% endfor %}
\end{thebibliography}
{% endif %}

\end{document}
"""

# IEEE Journal Template
IEEE_JOURNAL_TEMPLATE = r"""
\documentclass[journal]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{caption}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage[export]{adjustbox}
\usepackage{cite}
\usepackage{balance}

\title{<< title >>}
\author{
{% if authors %}
{% for author in authors %}
<< author.name >>{% if author.membership %}, \IEEEmembership{<< author.membership >>}{% endif %}
{% if author.affiliation %}
\thanks{<< author.name >> is with << author.affiliation >>. E-mail: << author.email >>}
{% endif %}
{% if not loop.last %}, {% endif %}
{% endfor %}
{% endif %}
}

\markboth{Journal Name, Vol. XX, No. XX, Month Year}
{Author \MakeLowercase{\textit{et al.}}: Paper Title}

\begin{document}
\maketitle

{% if abstract %}
\begin{abstract}
<< abstract >>
\end{abstract}
{% endif %}

{% if keywords %}
\begin{IEEEkeywords}
<< keywords >>
\end{IEEEkeywords}
{% endif %}

\IEEEpeerreviewmaketitle

{% for section in sections %}
\section{<< section.heading >>}
<< section.content >>

{% for sub in section.subsections %}
\subsection{<< sub.heading >>}
<< sub.content >>
{% endfor %}
{% endfor %}

{% if references %}
\begin{thebibliography}{99}
{% for ref in references %}
\bibitem{ref<< loop.index >>} << ref >>
{% endfor %}
\end{thebibliography}
{% endif %}

\balance
\end{document}
"""

IEEE_TRANSACTIONS_TEMPLATE = r"""
\documentclass[journal]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{caption}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage[export]{adjustbox}
\usepackage{cite}
\usepackage{color}

\title{<< title >>}
\author{
{% if authors %}
{% for author in authors %}
<< author.name >>{% if author.membership %}, \IEEEmembership{<< author.membership >>}{% endif %}
{% if author.affiliation %}
\thanks{Manuscript received Month Date, Year; revised Month Date, Year. << author.name >> is with << author.affiliation >> (e-mail: << author.email >>).}
{% endif %}
{% if not loop.last %}, {% endif %}
{% endfor %}
{% endif %}
}

\markboth{IEEE Transactions on Subject, Vol. XX, No. XX, Month Year}
{Author \MakeLowercase{\textit{et al.}}: Paper Title}

\begin{document}
\maketitle

{% if abstract %}
\begin{abstract}
<< abstract >>
\end{abstract}
{% endif %}

{% if keywords %}
\begin{IEEEkeywords}
<< keywords >>
\end{IEEEkeywords}
{% endif %}

\IEEEpeerreviewmaketitle

{% for section in sections %}
{% if loop.first %}
\section{<< section.heading >>}
\IEEEPARstart{T}{his} is where the actual content begins with a proper drop cap. << section.content >>
{% else %}
\section{<< section.heading >>}
<< section.content >>
{% endif %}

{% for sub in section.subsections %}
\subsection{<< sub.heading >>}
<< sub.content >>
{% endfor %}
{% endfor %}

\section*{Acknowledgment}
The authors would like to thank the anonymous reviewers for their valuable comments and suggestions.

{% if references %}
\begin{thebibliography}{99}
{% for ref in references %}
\bibitem{ref<< loop.index >>} << ref >>
{% endfor %}
\end{thebibliography}
{% endif %}

\begin{IEEEbiography}[{\includegraphics[width=1in,height=1.25in,clip,keepaspectratio]{photo}}]{Author Name}
Biography text here. The author received the B.S. degree from University in Year, and the Ph.D. degree from University in Year. His research interests include...
\end{IEEEbiography}

\end{document}
"""




# IEEE Letters Template
IEEE_LETTERS_TEMPLATE = r"""
\documentclass[journal,compsoc]{IEEEtran}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{textcomp}
\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{caption}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage[export]{adjustbox}
\usepackage{cite}

\title{<< title >>}
\author{
{% if authors %}
{% for author in authors %}
<< author.name >>{% if author.membership %}, \IEEEmembership{<< author.membership >>}{% endif %}
{% if not loop.last %}, {% endif %}
{% endfor %}
{% endif %}
}

\markboth{IEEE Letters Subject, Vol. XX, No. XX, Month Year}{}

\begin{document}
\maketitle

{% if abstract %}
\begin{abstract}
<< abstract >>
\end{abstract}
{% endif %}

{% if keywords %}
\begin{IEEEkeywords}
<< keywords >>
\end{IEEEkeywords}
{% endif %}

{% for section in sections %}
{% if loop.first %}
\IEEEPARstart{<< section.content[0] >>}{<< section.content[1:10] >>}<< section.content[10:] >>
{% else %}
\section{<< section.heading >>}
<< section.content >>
{% endif %}

{% for sub in section.subsections %}
\subsection{<< sub.heading >>}
<< sub.content >>
{% endfor %}
{% endfor %}

{% if references %}
\begin{thebibliography}{99}
{% for ref in references %}
\bibitem{ref<< loop.index >>} << ref >>
{% endfor %}
\end{thebibliography}
{% endif %}

\end{document}
"""

# Template dictionary
TEMPLATES = {
    'conference': IEEE_CONFERENCE_TEMPLATE,
    'journal': IEEE_JOURNAL_TEMPLATE,
    'transactions': IEEE_TRANSACTIONS_TEMPLATE,
    'letter': IEEE_LETTERS_TEMPLATE
}

def unicode_to_latex(text):
    """Convert common Unicode characters to LaTeX equivalents"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Common mathematical symbols
    unicode_replacements = {
        '∈': r'$\in$',
        '∉': r'$\notin$',
        '∀': r'$\forall$',
        '∃': r'$\exists$',
        '∞': r'$\infty$',
        '≤': r'$\leq$',
        '≥': r'$\geq$',
        '≠': r'$\neq$',
        '≈': r'$\approx$',
        '±': r'$\pm$',
        '×': r'$\times$',
        '÷': r'$\div$',
        '→': r'$\rightarrow$',
        '←': r'$\leftarrow$',
        '↔': r'$\leftrightarrow$',
        '⊂': r'$\subset$',
        '⊃': r'$\supset$',
        '⊆': r'$\subseteq$',
        '⊇': r'$\supseteq$',
        '∩': r'$\cap$',
        '∪': r'$\cup$',
        '∅': r'$\emptyset$',
        '∑': r'$\sum$',
        '∏': r'$\prod$',
        '∫': r'$\int$',
        '√': r'$\sqrt{}$',
        'α': r'$\alpha$',
        'β': r'$\beta$',
        'γ': r'$\gamma$',
        'δ': r'$\delta$',
        'ε': r'$\varepsilon$',
        'θ': r'$\theta$',
        'λ': r'$\lambda$',
        'μ': r'$\mu$',
        'π': r'$\pi$',
        'σ': r'$\sigma$',
        'φ': r'$\phi$',
        'ψ': r'$\psi$',
        'ω': r'$\omega$',
        'Α': r'$A$',
        'Β': r'$B$',
        'Γ': r'$\Gamma$',
        'Δ': r'$\Delta$',
        'Θ': r'$\Theta$',
        'Λ': r'$\Lambda$',
        'Π': r'$\Pi$',
        'Σ': r'$\Sigma$',
        'Φ': r'$\Phi$',
        'Ψ': r'$\Psi$',
        'Ω': r'$\Omega$',
        
        # Punctuation and symbols
        '"': r'``',
        '"': r"''",
        ''': r"`",
        ''': r"'",
        '–': r'--',
        '—': r'---',
        '−': r'$-$',  # Unicode minus sign
        '…': r'\ldots',
        '°': r'$^\circ$',
        '§': r'\S{}',
        '¶': r'\P{}',
        '©': r'\copyright{}',
        '®': r'\textregistered{}',
        '™': r'\texttrademark{}',
        
        # Fractions
        '½': r'$\frac{1}{2}$',
        '⅓': r'$\frac{1}{3}$',
        '¼': r'$\frac{1}{4}$',
        '¾': r'$\frac{3}{4}$',
        '⅕': r'$\frac{1}{5}$',
        '⅙': r'$\frac{1}{6}$',
        '⅛': r'$\frac{1}{8}$',
        
        # Superscripts and subscripts (common ones)
        '²': r'$^2$',
        '³': r'$^3$',
        '¹': r'$^1$',
        '⁰': r'$^0$',
        '⁴': r'$^4$',
        '⁵': r'$^5$',
        '⁶': r'$^6$',
        '⁷': r'$^7$',
        '⁸': r'$^8$',
        '⁹': r'$^9$',
        
        # Currency
        '€': r'\texteuro{}',
        '£': r'\pounds{}',
        '¥': r'\textyen{}',
        '¢': r'\textcent{}',
    }
    
    # Apply replacements
    for unicode_char, latex_equiv in unicode_replacements.items():
        text = text.replace(unicode_char, latex_equiv)
    
    return text

def latex_escape(text):
    """Enhanced LaTeX escaping with Unicode handling"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # First handle Unicode characters
    text = unicode_to_latex(text)
    
    # Then handle standard LaTeX special characters
    replacements = {
        '&': r'\&', 
        '%': r'\%', 
        '$': r'\$', 
        '#': r'\#',
        '_': r'\_', 
        '{': r'\{', 
        '}': r'\}', 
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', 
        '\\': r'\textbackslash{}'
    }
    
    # Sort by length (longest first) to avoid partial replacements
    pattern = re.compile('|'.join(re.escape(k) for k in sorted(replacements.keys(), key=len, reverse=True)))
    text = pattern.sub(lambda m: replacements[m.group()], text)
    
    return text

def clean_unicode_text(text):
    """Clean and normalize Unicode text for LaTeX compatibility"""
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # Normalize Unicode (NFKD: canonical decomposition, then canonical combining)
    text = unicodedata.normalize('NFKD', text)
    
    # Remove combining characters that might cause issues
    text = ''.join(char for char in text if not unicodedata.combining(char))
    
    # Remove zero-width characters
    zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff', '\u2060']
    for char in zero_width_chars:
        text = text.replace(char, '')
    
    return text

def convert_to_png(src, dest):
    try:
        with Image.open(src) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(dest, 'PNG')
        return True
    except Exception as e:
        print(f"[ERROR] Failed to convert image {src}: {e}")
        return False

def is_valid_png(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
            return img.format == 'PNG'
    except Exception:
        return False

image_pattern = re.compile(r'\[IMAGE:\s*([^\]]+)\]')
table_pattern = re.compile(r'\[TABLE:\s*([^\]]+)\]')

def render_images(content, temp_image_dir, images_data=None):
    import base64
    import uuid
    import os
    from PIL import Image
    import io
    
    def replace_image(match):
        img_path = match.group(1).strip()
        
        print(f"[DEBUG] Processing image path: {img_path[:100]}...")
        
        # Handle base64 data URLs (uploaded images)
        if img_path.startswith('data:image/'):
            try:
                print("[DEBUG] Processing base64 image")
                
                # Extract the image format and base64 data
                header, encoded = img_path.split(',', 1)
                image_format = header.split('/')[1].split(';')[0]
                
                # Decode base64 data to binary
                image_data = base64.b64decode(encoded)
                
                # Generate unique filename
                filename = f"uploaded_{uuid.uuid4().hex[:8]}.png"
                full_dest = os.path.join(temp_image_dir, filename)
                
                print(f"[DEBUG] Saving base64 image to: {full_dest}")
                
                # Convert and save as PNG
                if image_format.lower() in ['jpeg', 'jpg']:
                    img = Image.open(io.BytesIO(image_data))
                    img = img.convert('RGB')
                    img.save(full_dest, 'PNG')
                else:
                    with open(full_dest, 'wb') as f:
                        f.write(image_data)
                
                print(f"[DEBUG] Image saved: {os.path.exists(full_dest)}, Size: {os.path.getsize(full_dest) if os.path.exists(full_dest) else 0} bytes")
                
                # Get image metadata
                img_size = 'medium'
                img_caption = "Uploaded Image"
                
                if images_data:
                    for img_data in images_data:
                        if img_data.get('path') == img_path:
                            img_size = img_data.get('size', 'medium')
                            img_caption = latex_escape(img_data.get('caption', img_caption))
                            break
                
                # Generate LaTeX code
                alignment = r"\centering"
                width = {"small": "0.3", "medium": "0.5", "large": "0.8"}[img_size]
                
                latex_code = (
                    r"\begin{figure}[H]" + "\n"
                    f"{alignment}" + "\n"
                    f"\\includegraphics[width={width}\\textwidth]{{{filename}}}" + "\n"
                    f"\\caption{{{img_caption}}}" + "\n"
                    r"\end{figure}" + "\n"
                )
                
                print(f"[DEBUG] Generated LaTeX for base64 image: \\includegraphics[width={width}\\textwidth]{{{filename}}}")
                return latex_code
                
            except Exception as e:
                print(f"[ERROR] Failed to process base64 image: {e}")
                return r"\textbf{[Base64 image processing failed]}"
        
        # Handle file path images
        else:
            if img_path.startswith('/static/'):
                full_src = img_path.lstrip('/')
            else:
                full_src = img_path.lstrip("/\\")
            
            filename = os.path.basename(img_path)
            full_dest = os.path.join(temp_image_dir, filename)
            
            print(f"[DEBUG] Processing file image: {full_src} -> {full_dest}")

            # Get image metadata
            img_size = 'medium'
            img_caption = f"Image: {latex_escape(filename)}"
            
            if images_data:
                for img_data in images_data:
                    if img_data.get('path') == img_path or img_data.get('filename') == filename:
                        img_size = img_data.get('size', 'medium')
                        img_caption = latex_escape(img_data.get('caption', img_caption))
                        break

            if os.path.exists(full_src):
                try:
                    if is_valid_png(full_src):
                        shutil.copy(full_src, full_dest)
                    else:
                        if not convert_to_png(full_src, full_dest):
                            return r"\textbf{[Image conversion failed]}"
                    
                    print(f"[DEBUG] File image copied: {os.path.exists(full_dest)}")
                    
                    # Generate LaTeX code
                    alignment = r"\centering"
                    width = {"small": "0.3", "medium": "0.5", "large": "0.8"}[img_size]
                    
                    latex_code = (
                        r"\begin{figure}[H]" + "\n"
                        f"{alignment}" + "\n"
                        f"\\includegraphics[width={width}\\textwidth]{{{filename}}}" + "\n"
                        f"\\caption{{{img_caption}}}" + "\n"
                        r"\end{figure}" + "\n"
                    )
                    
                    print(f"[DEBUG] Generated LaTeX for file image: \\includegraphics[width={width}\\textwidth]{{{filename}}}")
                    return latex_code
                    
                except Exception as e:
                    print(f"[ERROR] Failed to process file image: {e}")
                    return r"\textbf{[Image processing failed]}"
            else:
                print(f"[ERROR] Image file not found: {full_src}")
                return r"\textbf{[Image not found]}"
    
    # Apply the replacement
    result = image_pattern.sub(replace_image, content)
    print(f"[DEBUG] Image replacement complete. Original length: {len(content)}, New length: {len(result)}")
    return result


def render_tables(content, table_data):
    def replace_table(match):
        table_id = match.group(1).strip()
        
        if table_id in table_data:
            table = table_data[table_id]
            if not table or not table[0]:
                return r"\textbf{[Empty table]}"
            
            col_count = len(table[0])
            # Use table* for two-column spanning in IEEE format
            latex = "\\begin{table*}[t]\n\\centering\n"
            latex += "\\begin{tabular}{|" + "|".join(["c"] * col_count) + "|}\n"
            latex += "\\hline\n"
            
            for row in table:
                escaped_cells = [latex_escape(cell) for cell in row]
                latex += " & ".join(escaped_cells) + " \\\\\n\\hline\n"
            
            latex += "\\end{tabular}\n"
            latex += "\\caption{Table}\n"
            latex += "\\end{table*}\n"
            
            return latex
        else:
            return r"\textbf{[Table not found]}"
    
    return table_pattern.sub(replace_table, content)

def safe_latex_escape(text, table_data):
    """
    Enhanced LaTeX escaping that handles Unicode and preserves LaTeX commands
    """
    if not isinstance(text, str):
        return str(text) if text is not None else ""
    
    # First clean and normalize Unicode
    text = clean_unicode_text(text)
    
    parts = []
    current_pos = 0
    
    # Find LaTeX figure and table blocks, and math mode content
    latex_blocks_pattern = re.compile(r'(\\begin\{(figure|table\*?)\}.*?\\end\{\2\}|\$[^$]*\$)', re.DOTALL)
    
    for match in latex_blocks_pattern.finditer(text):
        # Add escaped text before the LaTeX block
        if match.start() > current_pos:
            before_text = text[current_pos:match.start()]
            parts.append(latex_escape(before_text))
        
        # Add the LaTeX block without escaping
        parts.append(match.group())
        current_pos = match.end()
    
    # Add any remaining text after the last LaTeX block
    if current_pos < len(text):
        remaining_text = text[current_pos:]
        parts.append(latex_escape(remaining_text))
    
    return ''.join(parts)

def parse_authors_from_text(authors_list):
    """Parse author information from text"""
    if not authors_list:
        return []
    
    authors = []
    for author_text in authors_list:
        # Basic parsing - you can make this more sophisticated
        author_info = {
            'name': author_text.split('@')[0].strip() if '@' in author_text else author_text.strip(),
            'email': author_text.split('@')[1].split()[0] + '@' + author_text.split('@')[1].split()[1] if '@' in author_text else '',
            'affiliation': 'University/Institution',  # Default
            'membership': 'Student Member'  # Default
        }
        authors.append(author_info)
    
    return authors


# Add this function before generate_pdf_from_data in latex_formatter.py
def clean_content_for_parstart(content):
    """Extract clean text content for IEEEPARstart, avoiding LaTeX commands"""
    if not content or not isinstance(content, str):
        return content
    
    # Remove figure environments and their content
    import re
    clean_text = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', content, flags=re.DOTALL)
    clean_text = re.sub(r'\\includegraphics.*?\n', '', clean_text)
    clean_text = re.sub(r'\\caption\{.*?\}', '', clean_text)
    clean_text = re.sub(r'\\centering\s*', '', clean_text)
    clean_text = clean_text.strip()
    
    return clean_text



def generate_pdf_from_data(parsed_data, template_type='conference', output_path="static/temp.pdf"):
    try:
        from pathlib import Path
        import tempfile
        import subprocess
        import copy

        data = copy.deepcopy(parsed_data)
        table_data = data.get("table_data", {})

        # Get the selected template
        if template_type == 'journal':
            template_code = IEEE_JOURNAL_TEMPLATE
        elif template_type == 'transactions': 
            template_code = IEEE_TRANSACTIONS_TEMPLATE
        elif template_type == 'letter':
            template_code = IEEE_LETTERS_TEMPLATE
        else:
            template_code = IEEE_CONFERENCE_TEMPLATE  # default
        
        print(f"[DEBUG] Using template: {template_type}")
        print(f"[DEBUG] Processing {len(data.get('sections', []))} sections")

        # Enhanced escaping for basic fields
        data["title"] = safe_latex_escape(data.get("title", "Untitled Document"), {})
        data["abstract"] = safe_latex_escape(data.get("abstract", ""), {})
        data["keywords"] = safe_latex_escape(data.get("keywords", ""), {})
        
        # Parse authors
        authors_text = data.get("authors", [])
        if isinstance(authors_text, list) and len(authors_text) > 0 and isinstance(authors_text[0], str):
            # Convert old string format to new dict format
            data["authors"] = parse_authors_from_text(authors_text)
        elif not isinstance(data.get("authors", []), list) or len(data.get("authors", [])) == 0:
            data["authors"] = []

        with tempfile.TemporaryDirectory() as tmpdir:
            print(f"[INFO] Working in temp directory: {tmpdir}")
            print(f"[INFO] Using template: {template_type}")
            
            # Process sections with enhanced image handling
            for section_idx, section in enumerate(data.get("sections", [])):
                section_heading = section.get('heading', f'Section {section_idx + 1}')
                print(f"[DEBUG] Processing section: {section_heading}")
                
                section["heading"] = safe_latex_escape(section.get("heading", ""), {})
                raw_content = section.get("content", "")

                # Get images data for this section
                section_images = section.get("images", [])
                if section_images:
                    print(f"[DEBUG] Section '{section_heading}' has {len(section_images)} images")
                    for i, img in enumerate(section_images):
                        img_path = img.get('path', '')
                        img_caption = img.get('caption', f'Figure {i+1}')
                        print(f"[DEBUG] Image {i}: {img_path[:100]}...")
                        print(f"[DEBUG] Image caption: {img_caption}")
                        
                        # Create explicit image placeholder
                        image_placeholder = f"[IMAGE: {img_path}]"
                        
                        # Add image placeholder to content if not already present
                        if image_placeholder not in raw_content:
                            raw_content += f"\n\n{image_placeholder}\n\n"
                            print(f"[DEBUG] Added placeholder: {image_placeholder}")
                        else:
                            print(f"[DEBUG] Placeholder already exists in content")

                # Then in generate_pdf_from_data, add this before template rendering:
                if template_type == 'transactions' and data.get("sections"):
                    first_section = data["sections"][0]
                    if first_section.get("content"):
                        clean_first_content = clean_content_for_parstart(first_section["content"])
                        first_section["clean_content"] = clean_first_content

                
                # Process inline content first
                print(f"[DEBUG] Raw content length: {len(raw_content)} characters")
                
                # Render images first
                rendered_content = render_images(raw_content, tmpdir, section_images)
                print(f"[DEBUG] After image rendering: {len(rendered_content)} characters")
                
                # Then render tables
                rendered_content = render_tables(rendered_content, table_data)
                print(f"[DEBUG] After table rendering: {len(rendered_content)} characters")
                
                # Finally, safely escape (preserving LaTeX commands)
                section["content"] = safe_latex_escape(rendered_content, table_data)
                print(f"[DEBUG] Final content length: {len(section['content'])} characters")
                
                # Process subsections
                for sub in section.get("subsections", []):
                    sub["heading"] = safe_latex_escape(sub.get("heading", ""), {})
                    raw_sub_content = sub.get("content", "")
                    rendered_sub = render_images(raw_sub_content, tmpdir)
                    rendered_sub = render_tables(rendered_sub, table_data)
                    sub["content"] = safe_latex_escape(rendered_sub, table_data)

            # Process references with enhanced escaping
            data["references"] = [safe_latex_escape(ref, {}) for ref in data.get("references", [])]

            # Render LaTeX
            env = Environment(
                loader=BaseLoader(),
                variable_start_string='<<',
                variable_end_string='>>',
                autoescape=False
            )
            # template = env.from_string(template_code)





            template = env.from_string(template_code)

            tex_code = template.render(**data)

            # Save .tex file for debugging
            tex_path = Path(tmpdir) / "paper.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_code)
            
            print(f"[INFO] LaTeX file written to: {tex_path}")
            
            # Debug: Check if images are in tex code
            image_count = tex_code.count('\\includegraphics')
            print(f"[DEBUG] Found {image_count} \\includegraphics commands in LaTeX")

            # Run pdflatex
            for run_num in [1, 2, 3]:
                print(f"[INFO] Running pdflatex (pass {run_num})")
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=tmpdir
                )
                
                # Only fail on the final pass
                if result.returncode != 0 and run_num == 3:
                    error_log = result.stdout.decode("utf-8", errors="ignore") + "\n" + result.stderr.decode("utf-8", errors="ignore")
                    print(f"[ERROR] pdflatex failed on final pass")
                    print(error_log)
                    return {
                        "error": f"LaTeX compilation failed on pass {run_num}",
                        "log": error_log,
                        "tex_code": tex_code
                    }

            # Check if PDF was generated
            pdf_path = Path(tmpdir) / "paper.pdf"
            if pdf_path.exists():
                os.makedirs("static", exist_ok=True)
                shutil.copy(pdf_path, output_path)
                print(f"[SUCCESS] PDF generated: {output_path}")
                return {"success": True}
            else:
                log_output = result.stdout.decode("utf-8", errors="ignore") + "\n" + result.stderr.decode("utf-8", errors="ignore")
                return {
                    "error": "LaTeX ran but PDF not generated",
                    "log": log_output,
                    "tex_code": tex_code
                }

    except FileNotFoundError as e:
        return {"error": f"Missing executable: {e.filename}. Please install LaTeX (texlive-full or similar)"}
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Unexpected error: {str(e)}"}
