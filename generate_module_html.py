import json
import re
import html
import os

def clean_and_format_html(raw_html):
    if not raw_html:
        return ""

    # Reemplazar nbsp y espacios raros
    cleaned = raw_html.replace('\\&nbsp;', ' ').replace('&nbsp;', ' ').replace('\xa0', ' ')

    # Limpiar atributos que ensucian el marcado
    cleaned = re.sub(r' is-upgraded=""', '', cleaned)
    cleaned = re.sub(r' translate="no"', '', cleaned)
    cleaned = re.sub(r' dir="ltr"', '', cleaned)
    cleaned = re.sub(r' role="[^"]*"', '', cleaned)

    # Formatear bloques de código <pre>
    def fix_pre(match):
        content = match.group(1)
        content = content.strip()
        return f'<pre><code>{content}</code></pre>'

    cleaned = re.sub(r'<pre[^>]*>(.*?)</pre>', fix_pre, cleaned, flags=re.DOTALL)

    # Convertir notas y asides en callouts atractivos
    cleaned = re.sub(r'<aside[^>]*class="[^"]*notice[^"]*"[^>]*>', '<div class="callout callout-info">', cleaned)
    cleaned = re.sub(r'<aside[^>]*class="[^"]*caution[^"]*"[^>]*>', '<div class="callout callout-warning">', cleaned)
    cleaned = re.sub(r'<aside[^>]*class="[^"]*warning[^"]*"[^>]*>', '<div class="callout callout-danger">', cleaned)
    cleaned = re.sub(r'<aside[^>]*>', '<div class="callout">', cleaned)
    cleaned = cleaned.replace('</aside>', '</div>')

    return cleaned

def generate_module_html():
    with open("gcp_docs_data.json", "r", encoding="utf-8") as f:
        modules = json.load(f)

    for mod in modules:
        mod_id = mod["id"]
        mod_title = mod["title"]
        pages = mod["pages"]

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(mod_title)}</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            color: #202124;
            line-height: 1.6;
            font-size: 10pt;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .cover-page {{
            page-break-after: always;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100%;
            min-height: 230mm;
            text-align: center;
            border: 2px solid #1a73e8;
            border-radius: 8px;
            padding: 40px 20px;
            box-sizing: border-box;
        }}

        .cover-badge {{
            background-color: #e8f0fe;
            color: #1a73e8;
            font-weight: bold;
            font-size: 11pt;
            padding: 6px 16px;
            border-radius: 16px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 25px;
        }}

        .cover-title {{
            color: #1a73e8;
            font-size: 26pt;
            font-weight: 700;
            margin-bottom: 20px;
            line-height: 1.25;
        }}

        .cover-subtitle {{
            color: #5f6368;
            font-size: 13pt;
            margin-bottom: 40px;
            max-width: 80%;
        }}

        .cover-footer {{
            margin-top: auto;
            font-size: 9pt;
            color: #70757a;
            border-top: 1px solid #dadce0;
            padding-top: 15px;
            width: 80%;
        }}

        .toc-container {{
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            border-radius: 8px;
            padding: 20px 25px;
            margin-bottom: 35px;
            page-break-after: always;
        }}

        .toc-title {{
            font-size: 14pt;
            font-weight: bold;
            color: #1a73e8;
            margin-top: 0;
            margin-bottom: 15px;
            border-bottom: 2px solid #1a73e8;
            padding-bottom: 8px;
        }}

        .toc-list {{
            list-style-type: none;
            padding-left: 0;
            margin: 0;
        }}

        .toc-list li {{
            margin-bottom: 10px;
            font-size: 10.5pt;
        }}

        .toc-list a {{
            color: #1a73e8;
            text-decoration: none;
            font-weight: 500;
        }}

        .page-section {{
            margin-bottom: 40px;
            page-break-before: auto;
        }}

        h1.section-header {{
            color: #1a73e8;
            font-size: 18pt;
            border-bottom: 2px solid #e8eaed;
            padding-bottom: 8px;
            margin-top: 30px;
            margin-bottom: 20px;
            page-break-after: avoid;
        }}

        h2 {{
            color: #202124;
            font-size: 14pt;
            margin-top: 22px;
            margin-bottom: 12px;
            page-break-after: avoid;
        }}

        h3 {{
            color: #3c4043;
            font-size: 12pt;
            margin-top: 18px;
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

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9pt;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid #dadce0;
            padding: 8px 12px;
            text-align: left;
        }}

        th {{
            background-color: #f1f3f4;
            color: #202124;
            font-weight: bold;
        }}

        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        pre {{
            background-color: #282c34;
            color: #abb2bf;
            border-radius: 6px;
            padding: 12px 15px;
            overflow-x: auto;
            font-family: "Roboto Mono", "Courier New", Courier, monospace;
            font-size: 8.5pt;
            line-height: 1.45;
            margin: 15px 0;
            white-space: pre-wrap;
            word-break: break-all;
            page-break-inside: avoid;
        }}

        code {{
            font-family: "Roboto Mono", "Courier New", Courier, monospace;
            background-color: #f1f3f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 9pt;
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

        .callout-warning {{
            background-color: #fef7e0;
            border-left-color: #f9ab00;
        }}

        .callout-danger {{
            background-color: #fce8e6;
            border-left-color: #d93025;
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

        .source-link {{
            font-size: 8.5pt;
            color: #70757a;
            margin-bottom: 15px;
            font-style: italic;
        }}
    </style>
</head>
<body>

    <div class="cover-page">
        <div class="cover-badge">Google Cloud Documentation</div>
        <div class="cover-title">{html.escape(mod_title)}</div>
        <div class="cover-subtitle">Manual y Guía Completa de Referencia Extraída de la Documentación Oficial de Google Cloud</div>
        <div class="cover-footer">
            Idioma: Español (es-419) | Formato Modular de Documentación Técnica
        </div>
    </div>

    <div class="toc-container">
        <div class="toc-title">Índice del Módulo</div>
        <ul class="toc-list">
"""

        for idx, page_item in enumerate(pages):
            p_title = html.escape(page_item["page_title"])
            html_content += f'            <li><a href="#section-{idx + 1}">{idx + 1}. {p_title}</a></li>\n'

        html_content += """        </ul>
    </div>

    <div class="module-body">
"""

        for idx, page_item in enumerate(pages):
            p_title = html.escape(page_item["page_title"])
            p_url = html.escape(page_item["url"])
            p_html = clean_and_format_html(page_item["html"])

            html_content += f"""
        <div class="page-section" id="section-{idx + 1}">
            <h1 class="section-header">{idx + 1}. {p_title}</h1>
            <div class="source-link">Fuente oficial: <a href="{p_url}">{p_url}</a></div>
            <div class="section-content">
                {p_html}
            </div>
        </div>
"""

        html_content += """
    </div>

</body>
</html>
"""

        out_filename = f"{mod_id}.html"
        with open(out_filename, "w", encoding="utf-8") as out_f:
            out_f.write(html_content)

        print(f"Generado {out_filename} ({len(html_content)} bytes)")

if __name__ == "__main__":
    generate_module_html()
