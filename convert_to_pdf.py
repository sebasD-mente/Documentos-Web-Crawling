import asyncio
import os
from playwright.async_api import async_playwright

async def html_to_pdf():
    html_path = os.path.abspath("documento.html")
    pdf_path = os.path.abspath("manual_administracion_y_seguridad_de_claves_de_api.pdf")

    print(f"Cargando HTML desde {html_path}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"file://{html_path}", wait_until="networkidle")

        print("Generando PDF con Playwright...")
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
            header_template='<div style="font-size: 8pt; font-family: Helvetica, Arial, sans-serif; color: #70757a; margin-left: 15mm; margin-right: 15mm; width: 100%; display: flex; justify-content: space-between;"><span>Administración y seguridad de claves de API - Manual</span><span>Google Codelabs</span></div>',
            footer_template='<div style="font-size: 8pt; font-family: Helvetica, Arial, sans-serif; color: #70757a; margin-left: 15mm; margin-right: 15mm; width: 100%; text-align: right;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'
        )

        await browser.close()
        print(f"PDF generado exitosamente en: {pdf_path}")

if __name__ == "__main__":
    asyncio.run(html_to_pdf())
