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
        env = Environment(
            loader=BaseLoader(),
            variable_start_string='<<',  # change delimiters to avoid conflict with LaTeX
            variable_end_string='>>',
            autoescape=False
        )
        template = env.from_string(IEEE_TEMPLATE)
        tex_code = template.render(**parsed_data)

        # Save .tex and compile
        import tempfile, subprocess, os
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "paper.tex"
            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(tex_code)

            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, str(tex_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                return {"error": result.stderr.decode("utf-8")}

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
        print("Subprocess failed:", e)
        return {"error": str(e)}

