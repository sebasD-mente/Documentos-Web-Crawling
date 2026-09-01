import json
import re
import html

def clean_and_format_step_html(raw_html):
    # Reemplazar entidades de espacio no separable y barra invertida pegada a &nbsp;
    cleaned = raw_html.replace('\\&nbsp;', '\\ ').replace('&nbsp;', ' ').replace('\xa0', ' ')

    # Remover etiquetas o atributos no deseados (como is-upgraded, translate, dir, etc.)
    cleaned = re.sub(r' is-upgraded=""', '', cleaned)
    cleaned = re.sub(r' translate="no"', '', cleaned)
    cleaned = re.sub(r' dir="ltr"', '', cleaned)

    # Remover enlaces internos vacíos o desordenados dentro de los títulos
    cleaned = re.sub(r'<h2[^>]*><a[^>]*>(.*?)</a></h2>', r'<h2>\1</h2>', cleaned)

    # Si hay bloques de código dentro de <pre>, formatear el contenido de pre adecuadamente
    def fix_pre(match):
        content = match.group(1)
        # Desescapar/escapar adecuadamente
        # Eliminar espacios innecesarios al inicio o final
        content = content.strip()
        return f'<pre><code>{content}</code></pre>'

    cleaned = re.sub(r'<pre[^>]*>(.*?)</pre>', fix_pre, cleaned, flags=re.DOTALL)

    # Convertir asides (como <aside class="special-notice">) en callouts bonitos
    cleaned = re.sub(r'<aside[^>]*class="[^"]*notice[^"]*"[^>]*>', '<div class="callout callout-info">', cleaned)
    cleaned = re.sub(r'<aside[^>]*>', '<div class="callout">', cleaned)
    cleaned = cleaned.replace('</aside>', '</div>')

    # Asegurar que las imágenes tengan URL completa si son relativas
    cleaned = re.sub(r'src="//', 'src="https://', cleaned)
    cleaned = re.sub(r'src="/', 'src="https://codelabs.developers.google.com/', cleaned)

    return cleaned

def generate_full_html():
    with open("scraped_codelab.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data["title"]
    author = data["author"]
    date = data["updated_date"]
    url = data["source_url"]

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
            @bottom-right {{
                content: counter(page);
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                font-size: 9pt;
                color: #5f6368;
            }}
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #202124;
            line-height: 1.6;
            font-size: 11pt;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .header-container {{
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 15px;
            margin-bottom: 25px;
        }}

        h1 {{
            color: #1a73e8;
            font-size: 24pt;
            margin-top: 0;
            margin-bottom: 10px;
            line-height: 1.2;
        }}

        .meta-info {{
            font-size: 10pt;
            color: #5f6368;
            margin-bottom: 5px;
        }}

        .meta-info span {{
            margin-right: 15px;
        }}

        .toc-container {{
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 15px 20px;
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}

        .toc-title {{
            font-size: 12pt;
            font-weight: bold;
            color: #3c4043;
            margin-top: 0;
            margin-bottom: 10px;
        }}

        .toc-list {{
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }}

        .toc-list li {{
            margin-bottom: 6px;
        }}

        .toc-list a {{
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }}

        .step-container {{
            margin-bottom: 35px;
            page-break-before: auto;
        }}

        h2 {{
            color: #202124;
            font-size: 16pt;
            border-bottom: 1px solid #e8eaed;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }}

        h3 {{
            color: #3c4043;
            font-size: 13pt;
            margin-top: 20px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}

        p {{
            margin-top: 0;
            margin-bottom: 12px;
            text-align: justify;
        }}

        ul, ol {{
            margin-top: 0;
            margin-bottom: 12px;
            padding-left: 24px;
        }}

        li {{
            margin-bottom: 6px;
        }}

        pre {{
            background-color: #f1f3f4;
            border: 1px solid #dadce0;
            border-left: 4px solid #1a73e8;
            border-radius: 4px;
            padding: 12px 15px;
            overflow-x: auto;
            font-family: "Roboto Mono", "Courier New", Courier, monospace;
            font-size: 9.5pt;
            line-height: 1.45;
            color: #202124;
            margin-top: 10px;
            margin-bottom: 15px;
            white-space: pre-wrap;
            word-break: break-all;
            page-break-inside: avoid;
        }}

        code {{
            font-family: "Roboto Mono", "Courier New", Courier, monospace;
            background-color: #f1f3f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 9.5pt;
            color: #c5221f;
        }}

        pre code {{
            background-color: transparent;
            padding: 0;
            color: inherit;
            font-size: inherit;
        }}

        .callout {{
            background-color: #e8f0fe;
            border-left: 4px solid #1a73e8;
            padding: 12px 15px;
            margin: 15px 0;
            border-radius: 0 4px 4px 0;
            page-break-inside: avoid;
        }}

        .callout-info {{
            background-color: #e8f0fe;
            border-left-color: #1a73e8;
        }}

        .callout p:last-child {{
            margin-bottom: 0;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 15px auto;
        }}

        .footer-note {{
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #dadce0;
            font-size: 8.5pt;
            color: #70757a;
            text-align: center;
        }}
    </style>
</head>
<body>

    <div class="header-container">
        <h1>{html.escape(title)}</h1>
        <div class="meta-info">
            <span><strong>Autor:</strong> {html.escape(author)}</span>
            <span><strong>Última actualización:</strong> {html.escape(date)}</span>
        </div>
        <div class="meta-info">
            <span><strong>Fuente:</strong> <a href="{html.escape(url)}">{html.escape(url)}</a></span>
        </div>
    </div>

    <div class="toc-container">
        <div class="toc-title">Contenido del Manual</div>
        <ul class="toc-list">
"""

    for step in data["steps"]:
        s_num = step["step_number"]
        s_label = html.escape(step["label"])
        html_content += f'            <li><a href="#step-{s_num}">{s_num}. {s_label}</a></li>\n'

    html_content += """        </ul>
    </div>

    <div class="content-body">
"""

    for step in data["steps"]:
        s_num = step["step_number"]
        s_label = html.escape(step["label"])
        s_html = clean_and_format_step_html(step["html"])

        html_content += f"""
        <div class="step-container" id="step-{s_num}">
            {s_html}
        </div>
"""

    html_content += f"""
    </div>

    <div class="footer-note">
        Documento escrapeado y generado automáticamente para Gemini Notebook / Fuente de información.<br>
        Origen: {html.escape(url)}
    </div>

</body>
</html>
"""

    with open("documento.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Archivo documento.html generado con éxito.")

if __name__ == "__main__":
    generate_full_html()
