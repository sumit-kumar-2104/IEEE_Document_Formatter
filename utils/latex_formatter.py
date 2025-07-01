from jinja2 import Environment, BaseLoader

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
  \bibitem{} << ref >>
  {% endfor %}
\end{thebibliography}

\end{document}
"""

def generate_pdf_from_data(parsed_data, output_path="static/temp.pdf"):
    try:
        from pathlib import Path
        import tempfile
        import subprocess
        import os

        # Setup Jinja2 template rendering with safe delimiters
        env = Environment(
            loader=BaseLoader(),
            variable_start_string='<<',
            variable_end_string='>>',
            autoescape=False
        )
        template = env.from_string(IEEE_TEMPLATE)
        tex_code = template.render(**parsed_data)

        # Debug: Print the generated LaTeX source
        print("[DEBUG] LaTeX source:\n", tex_code)

        # Create temporary directory and write .tex file
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "paper.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_code)

            # Compile LaTeX to PDF using pdflatex
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Debug: Show pdflatex output
            print("[DEBUG] STDOUT:\n", result.stdout.decode("utf-8"))
            print("[DEBUG] STDERR:\n", result.stderr.decode("utf-8"))

            if result.returncode != 0:
                return {
                    "error": f"LaTeX compilation failed:\n{result.stderr.decode('utf-8')}\n\n"
                             f"Log:\n{result.stdout.decode('utf-8')}"
                }

            # Move generated PDF to output path
            pdf_path = Path(tmpdir) / "paper.pdf"
            if pdf_path.exists():
                os.makedirs("static", exist_ok=True)
                os.replace(pdf_path, output_path)
                return {"success": True}
            else:
                return {"error": "PDF file not generated"}
    except FileNotFoundError as e:
        return {"error": f"Missing executable: {e.filename}. Is it installed and in your system PATH?"}
    except Exception as e:
        print("[ERROR] Subprocess failed:", e)
        return {"error": str(e)}
