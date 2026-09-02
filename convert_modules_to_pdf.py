import asyncio
import os
import glob
from playwright.async_api import async_playwright

async def convert_html_to_pdf():
    pdf_dir = os.path.abspath("documentacion_jules_pdf")
    os.makedirs(pdf_dir, exist_ok=True)

    html_files = sorted(glob.glob("html_output/*.html"))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for html_file in html_files:
            abs_html_path = os.path.abspath(html_file)
            filename_no_ext = os.path.splitext(os.path.basename(html_file))[0]
            pdf_path = os.path.join(pdf_dir, f"{filename_no_ext}.pdf")

            print(f"Convirtiendo {filename_no_ext}.html -> PDF...")

            page = await browser.new_page()
            await page.goto(f"file://{abs_html_path}", wait_until="networkidle")

            # PDF generation
            await page.pdf(
                path=pdf_path,
                format="A4",
                print_background=True,
                margin={
                    "top": "20mm",
                    "bottom": "20mm",
                    "left": "15mm",
                    "right": "15mm"
                },
                display_header_footer=True,
                header_template='<div style="font-size: 8pt; font-family: Helvetica, Arial, sans-serif; color: #9ca3af; margin-left: 15mm; margin-right: 15mm; width: 100%; display: flex; justify-content: space-between;"><span>Jules Agent Documentation</span><span>jules.google/docs</span></div>',
                footer_template='<div style="font-size: 8pt; font-family: Helvetica, Arial, sans-serif; color: #9ca3af; margin-left: 15mm; margin-right: 15mm; width: 100%; text-align: right;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
            )

            await page.close()
            print(f"  Guardado: {pdf_path}")

        await browser.close()

    print("\n¡Todos los PDFs fueron generados exitosamente en 'documentacion_jules_pdf/'!")

if __name__ == "__main__":
    asyncio.run(convert_html_to_pdf())
