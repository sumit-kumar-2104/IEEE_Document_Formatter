from jinja2 import Environment, BaseLoader
import re
import os
import shutil
from PIL import Image
from datetime import datetime, timezone

# Template for IEEE LaTeX with unique bibitem labels
IEEE_TEMPLATE = r"""
\documentclass[conference]{IEEEtran}
\usepackage{graphicx}
\usepackage{float}  % helps with image placement
\usepackage{amsmath}
\usepackage{caption}
\usepackage{hyperref}

\title{<< title >>}
\author{}

\begin{document}
\maketitle

\begin{abstract}
<< abstract >>
\end{abstract}

\begin{IEEEkeywords}
<< keywords >>
\end{IEEEkeywords}

{% for section in sections %}
\section{<< section.heading >>}
<< section.content >>

  {% for sub in section.subsections %}
  \subsection{<< sub.heading >>}
  << sub.content >>
  {% endfor %}
{% endfor %}

\begin{thebibliography}{99}
  {% for ref in references %}
  \bibitem{ref<< loop.index >>} << ref >>
  {% endfor %}
\end{thebibliography}

\end{document}
"""

# Escape LaTeX special characters
def latex_escape(text):
    if not isinstance(text, str):
        return text
    replacements = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\^{}', '\\': r'\textbackslash{}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    return pattern.sub(lambda m: replacements[m.group()], text)

# Convert image to PNG if needed
def convert_to_png(src, dest):
    try:
        with Image.open(src) as img:
            rgb_img = img.convert('RGB')
            rgb_img.save(dest, 'PNG')
        return True
    except Exception as e:
        print("[ERROR] Failed to convert image:", e)
        return False

# Validate PNG image
def is_valid_png(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
            return img.format == 'PNG'
    except Exception:
        print(f"[SKIP] Invalid image {filepath}")
        return False

# Updated image pattern: matches [IMAGE: path]
image_pattern = re.compile(r'\[IMAGE:\s*(.*?)\]')

def render_images(content, image_dir, temp_image_dir):
    def replace_image(match):
        img_path = match.group(1).strip()
        filename = os.path.basename(img_path)
        full_src = os.path.join(".", img_path.lstrip("/\\"))
        full_dest = os.path.join(temp_image_dir, filename)

        if os.path.exists(full_src):
            if is_valid_png(full_src):
                shutil.copy(full_src, full_dest)
            else:
                if not convert_to_png(full_src, full_dest):
                    return r"\textbf{[Image failed to render]}"
            return (
                r"\begin{figure}[H]\centering"
                f"\n\\includegraphics[width=0.5\\textwidth]{{{filename}}}"
                f"\n\\caption{{Image: {filename}}}"
                r"\end{figure}"
            )
        else:
            return r"\textbf{[Image not found]}"
    
    return image_pattern.sub(replace_image, content)



# Main PDF generation function
def generate_pdf_from_data(parsed_data, output_path="static/temp.pdf"):
    try:
        from pathlib import Path
        import tempfile
        import subprocess

        parsed_data["title"] = latex_escape(parsed_data.get("title", ""))
        parsed_data["abstract"] = latex_escape(parsed_data.get("abstract", ""))
        parsed_data["keywords"] = latex_escape(parsed_data.get("keywords", ""))

        with tempfile.TemporaryDirectory() as tmpdir:
            for section in parsed_data.get("sections", []):
                section["heading"] = latex_escape(section.get("heading", ""))

                # First render images, then escape text
                raw_content = section.get("content", "")
                rendered_content = render_images(raw_content, '', tmpdir)
                section["content"] = latex_escape(rendered_content)

                for sub in section.get("subsections", []):
                    sub["heading"] = latex_escape(sub.get("heading", ""))
                    raw_sub_content = sub.get("content", "")
                    rendered_sub = render_images(raw_sub_content, '', tmpdir)
                    sub["content"] = latex_escape(rendered_sub)

            # Escape references
            parsed_data["references"] = [latex_escape(ref) for ref in parsed_data.get("references", [])]

            # Render LaTeX
            env = Environment(
                loader=BaseLoader(),
                variable_start_string='<<',
                variable_end_string='>>',
                autoescape=False
            )
            template = env.from_string(IEEE_TEMPLATE)
            tex_code = template.render(**parsed_data)

            tex_path = Path(tmpdir) / "paper.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_code)

            # Run pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            pdf_path = Path(tmpdir) / "paper.pdf"
            if pdf_path.exists():
                os.makedirs("static", exist_ok=True)
                os.replace(pdf_path, output_path)
                return {"success": True}
            else:
                return {
                    "error": "LaTeX ran but PDF not generated.",
                    "log": result.stdout.decode("utf-8") + "\n" + result.stderr.decode("utf-8")
                }

    except FileNotFoundError as e:
        return {"error": f"Missing executable: {e.filename}. Is it installed and in your system PATH?"}
    except Exception as e:
        print("[ERROR] Subprocess failed:", e)
        return {"error": str(e)}

