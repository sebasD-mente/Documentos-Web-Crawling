import asyncio
import json
import os
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

async def convert_html_to_pdf():
    with open("gcp_docs_data.json", "r", encoding="utf-8") as f:
        modules = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for mod in modules:
            mod_id = mod["id"]
            mod_title = mod["title"]
            pdf_filename = mod["pdf_filename"]

            html_file_path = os.path.abspath(f"{mod_id}.html")
            pdf_file_path = os.path.abspath(pdf_filename)

            if not os.path.exists(html_file_path):
                logging.error(f"Archivo HTML no encontrado: {html_file_path}")
                continue

            logging.info(f"Cargando {html_file_path}...")
            await page.goto(f"file://{html_file_path}", wait_until="networkidle")

            # Header y Footer en template HTML para Playwright
            header_template = f'''
            <div style="font-size: 8pt; font-family: -apple-system, Helvetica, Arial, sans-serif; color: #70757a; margin-left: 15mm; margin-right: 15mm; width: 100%; display: flex; justify-content: space-between;">
                <span>{mod_title}</span>
                <span>Google Cloud Docs</span>
            </div>
            '''

            footer_template = '''
            <div style="font-size: 8pt; font-family: -apple-system, Helvetica, Arial, sans-serif; color: #70757a; margin-left: 15mm; margin-right: 15mm; width: 100%; text-align: right;">
                <span class="pageNumber"></span> / <span class="totalPages"></span>
            </div>
            '''

            logging.info(f"Generando PDF: {pdf_file_path}...")
            await page.pdf(
                path=pdf_file_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                },
                display_header_footer=True,
                header_template=header_template,
                footer_template=footer_template
            )

            file_size_mb = os.path.getsize(pdf_file_path) / (1024 * 1024)
            logging.info(f"PDF generado exitosamente: {pdf_filename} ({file_size_mb:.2f} MB)")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
