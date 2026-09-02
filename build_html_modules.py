import json
import re
import html
import os

def clean_and_format_html(raw_html):
    if not raw_html:
        return ""

    cleaned = raw_html

    # Replace class attributes or inline styles that might break layout
    # Keep pre, code, blockquote, callout, tables, lists, images
    cleaned = re.sub(r'class="astro-[a-z0-9]+"', '', cleaned)

    # Fix images with relative paths
    cleaned = re.sub(r'src="/', 'src="https://jules.google/', cleaned)

    # Fix internal links
    cleaned = re.sub(r'href="/docs/', 'href="https://jules.google/docs/', cleaned)

    # Clean pre tags for code blocks
    # Ensure pre blocks look clean and code tags inside them are styled
    def fix_pre(match):
        content = match.group(1)
        return f'<pre><code>{content}</code></pre>'

    # Clean up empty headers or leftover buttons
    cleaned = re.sub(r'<button[^>]*>.*?</button>', '', cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'<svg[^>]*>.*?</svg>', '', cleaned, flags=re.DOTALL)

    return cleaned

CSS_STYLES = """
@page {
    size: A4;
    margin: 20mm 15mm 20mm 15mm;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1f2937;
    line-height: 1.6;
    font-size: 10.5pt;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
}

.cover-page {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 80vh;
    text-align: center;
}

.cover-title {
    font-size: 28pt;
    font-weight: 800;
    color: #1a73e8;
    margin-bottom: 15px;
}

.cover-subtitle {
    font-size: 16pt;
    color: #4b5563;
    margin-bottom: 30px;
}

.cover-meta {
    font-size: 11pt;
    color: #6b7280;
    border-top: 1px solid #e5e7eb;
    padding-top: 15px;
}

.module-header {
    border-bottom: 3px solid #1a73e8;
    padding-bottom: 10px;
    margin-bottom: 25px;
}

h1 {
    color: #1a73e8;
    font-size: 22pt;
    margin-top: 0;
    margin-bottom: 15px;
}

h2 {
    color: #111827;
    font-size: 15pt;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 6px;
    margin-top: 25px;
    margin-bottom: 12px;
    page-break-after: avoid;
}

h3 {
    color: #374151;
    font-size: 12pt;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
}

p {
    margin-top: 0;
    margin-bottom: 12px;
}

ul, ol {
    margin-top: 0;
    margin-bottom: 12px;
    padding-left: 20px;
}

li {
    margin-bottom: 4px;
}

pre {
    background-color: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-left: 4px solid #1a73e8;
    border-radius: 4px;
    padding: 10px 12px;
    overflow-x: auto;
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    font-size: 9pt;
    line-height: 1.4;
    color: #111827;
    margin-top: 10px;
    margin-bottom: 15px;
    white-space: pre-wrap;
    word-break: break-all;
    page-break-inside: avoid;
}

code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    background-color: #f3f4f6;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 9pt;
    color: #d97706;
}

pre code {
    background-color: transparent;
    padding: 0;
    color: inherit;
    font-size: inherit;
}

blockquote, .callout {
    background-color: #eff6ff;
    border-left: 4px solid #2563eb;
    padding: 10px 14px;
    margin: 12px 0;
    border-radius: 0 4px 4px 0;
    page-break-inside: avoid;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 9.5pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #d1d5db;
    padding: 8px 10px;
    text-align: left;
}

th {
    background-color: #f9fafb;
    font-weight: 600;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 15px auto;
}

.toc-container {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 15px 20px;
    margin-bottom: 30px;
    page-break-inside: avoid;
}

.toc-title {
    font-size: 12pt;
    font-weight: bold;
    color: #1f2937;
    margin-bottom: 10px;
}

.toc-list {
    list-style-type: none;
    padding-left: 0;
    margin: 0;
}

.toc-list li {
    margin-bottom: 6px;
}

.toc-list a {
    color: #2563eb;
    text-decoration: none;
}

.page-break {
    page-break-before: always;
}

.footer-note {
    margin-top: 40px;
    padding-top: 15px;
    border-top: 1px solid #e5e7eb;
    font-size: 8.5pt;
    color: #9ca3af;
    text-align: center;
}
"""

def generate_html_files():
    with open("scraped_jules_docs.json", "r", encoding="utf-8") as f:
        modules_data = json.load(f)

    os.makedirs("html_output", exist_ok=True)

    # Generate individual module HTML files
    for idx, mod in enumerate(modules_data, start=1):
        mod_title = mod["title"]
        mod_id = mod["id"]

        html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>{html.escape(mod_title)} - Jules Documentation</title>
    <style>{CSS_STYLES}</style>
</head>
<body>

    <div class="cover-page">
        <div class="cover-title">Documentación Oficial de Jules</div>
        <div class="cover-subtitle">{html.escape(mod_title)}</div>
        <div class="cover-meta">
            Google Jules Agent Docs<br>
            Fuente: https://jules.google/docs
        </div>
    </div>

    <div class="toc-container">
        <div class="toc-title">Tabla de Contenido</div>
        <ul class="toc-list">
"""
        for p_idx, page in enumerate(mod["pages"], start=1):
            p_title = html.escape(page["title"])
            html_content += f'            <li><a href="#page-{p_idx}">{p_idx}. {p_title}</a></li>\n'

        html_content += """        </ul>
    </div>

    <div class="content-body">
"""

        for p_idx, page in enumerate(mod["pages"], start=1):
            p_title = html.escape(page["title"])
            p_url = html.escape(page["url"])
            p_html = clean_and_format_html(page["html"])

            page_break_class = "page-break" if p_idx > 1 else ""
            html_content += f"""
        <div class="page-container {page_break_class}" id="page-{p_idx}">
            <div class="module-header">
                <h2>{p_title}</h2>
                <div style="font-size: 8.5pt; color: #6b7280;">Fuente: {p_url}</div>
            </div>
            {p_html}
        </div>
"""

        html_content += f"""
    </div>

    <div class="footer-note">
        Documentación de Jules Agent - {html.escape(mod_title)}
    </div>

</body>
</html>
"""

        out_path = f"html_output/{mod_id}.html"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Generado: {out_path}")

    # Generate unified HTML file with ALL modules
    unified_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Documentación Completa de Jules Agent</title>
    <style>{CSS_STYLES}</style>
</head>
<body>

    <div class="cover-page">
        <div class="cover-title">Documentación Completa de Jules</div>
        <div class="cover-subtitle">Manual Exhaustivo de Usuario, API, CLI, Integraciones y Changelog</div>
        <div class="cover-meta">
            Google Jules Agent Docs<br>
            Fuente: https://jules.google/docs
        </div>
    </div>

    <div class="toc-container">
        <div class="toc-title">Índice General por Módulos</div>
        <ul class="toc-list">
"""

    for mod_idx, mod in enumerate(modules_data, start=1):
        mod_title = html.escape(mod["title"])
        unified_html += f'            <li><strong><a href="#mod-{mod_idx}">{mod_title}</a></strong>\n                <ul>\n'
        for p_idx, page in enumerate(mod["pages"], start=1):
            p_title = html.escape(page["title"])
            unified_html += f'                    <li><a href="#mod-{mod_idx}-page-{p_idx}">{p_title}</a></li>\n'
        unified_html += '                </ul>\n            </li>\n'

    unified_html += """        </ul>
    </div>

    <div class="content-body">
"""

    for mod_idx, mod in enumerate(modules_data, start=1):
        mod_title = html.escape(mod["title"])
        unified_html += f"""
        <div class="page-break" id="mod-{mod_idx}">
            <h1 style="border-bottom: 4px solid #1a73e8; padding-bottom: 12px; margin-top: 30px;">{mod_title}</h1>
        </div>
"""
        for p_idx, page in enumerate(mod["pages"], start=1):
            p_title = html.escape(page["title"])
            p_url = html.escape(page["url"])
            p_html = clean_and_format_html(page["html"])

            unified_html += f"""
        <div class="page-container page-break" id="mod-{mod_idx}-page-{p_idx}">
            <div class="module-header">
                <h2>{p_title}</h2>
                <div style="font-size: 8.5pt; color: #6b7280;">Módulo {mod_idx} | Fuente: {p_url}</div>
            </div>
            {p_html}
        </div>
"""

    unified_html += """
    </div>

    <div class="footer-note">
        Documentación Completa de Jules Agent - Google
    </div>

</body>
</html>
"""

    unified_path = "html_output/documentacion_completa_jules.html"
    with open(unified_path, "w", encoding="utf-8") as f:
        f.write(unified_html)
    print(f"Generado documento unificado: {unified_path}")

if __name__ == "__main__":
    generate_html_files()
