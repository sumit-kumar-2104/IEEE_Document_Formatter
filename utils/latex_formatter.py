from jinja2 import Environment, BaseLoader
import re

# Template for IEEE LaTeX with unique bibitem labels
IEEE_TEMPLATE = r"""
\documentclass[conference]{IEEEtran}
\usepackage{graphicx}
\usepackage{amsmath}
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

# Function to escape LaTeX special characters
def latex_escape(text):
    if not isinstance(text, str):
        return text
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replacements))
    return pattern.sub(lambda m: replacements[m.group()], text)

# Main function to generate IEEE PDF
def generate_pdf_from_data(parsed_data, output_path="static/temp.pdf"):
    try:
        from pathlib import Path
        import tempfile
        import subprocess
        import os

        # Escape all user content
        parsed_data["title"] = latex_escape(parsed_data.get("title", ""))
        parsed_data["abstract"] = latex_escape(parsed_data.get("abstract", ""))
        parsed_data["keywords"] = latex_escape(parsed_data.get("keywords", ""))
        parsed_data["sections"] = [
            {
                "heading": latex_escape(s["heading"]),
                "content": latex_escape(s["content"]),
                "subsections": [
                    {
                        "heading": latex_escape(sub["heading"]),
                        "content": latex_escape(sub["content"]),
                    } for sub in s.get("subsections", [])
                ]
            }
            for s in parsed_data.get("sections", [])
        ]
        parsed_data["references"] = [latex_escape(ref) for ref in parsed_data.get("references", [])]

        # Setup Jinja2 and render template
        env = Environment(
            loader=BaseLoader(),
            variable_start_string='<<',
            variable_end_string='>>',
            autoescape=False
        )
        template = env.from_string(IEEE_TEMPLATE)
        tex_code = template.render(**parsed_data)

        print("[DEBUG] LaTeX source:\n", tex_code)  # print generated LaTeX

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "paper.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_code)

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            print("[DEBUG] STDOUT:\n", result.stdout.decode("utf-8"))
            print("[DEBUG] STDERR:\n", result.stderr.decode("utf-8"))

            pdf_path = Path(tmpdir) / "paper.pdf"
            if pdf_path.exists():
                os.makedirs("static", exist_ok=True)
                os.replace(pdf_path, output_path)
                return {"success": True}
            else:
                return {
                    "error": "LaTeX ran but PDF not generated.",
                    "log": result.stdout.decode("utf-8")
                }

    except FileNotFoundError as e:
        return {"error": f"Missing executable: {e.filename}. Is it installed and in your system PATH?"}
    except Exception as e:
        print("[ERROR] Subprocess failed:", e)
        return {"error": str(e)}
