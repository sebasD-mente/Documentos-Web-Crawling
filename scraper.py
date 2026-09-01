import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_codelab():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        url = "https://codelabs.developers.google.com/api-key-management?hl=es-419#0"
        print(f"Navegando a {url}...")
        await page.goto(url, wait_until="networkidle")

        # Extraer metadatos generales
        main_title = await page.evaluate('''() => {
            let el = document.querySelector('google-codelab-about .token');
            return el ? el.innerText.trim() : "Administración y seguridad de claves de API";
        }''')

        updated_date = "22 jun 2026"
        author = "Leonid Yankulin"

        print(f"Título: {main_title}")
        print(f"Fecha: {updated_date}")
        print(f"Autor: {author}")

        # Extraer cada paso
        steps_els = await page.query_selector_all('google-codelab-step')
        steps_data = []

        for idx, step_el in enumerate(steps_els):
            label = await step_el.get_attribute('label')

            # Obtener el HTML interno de las instrucciones
            step_html = await step_el.evaluate('''el => {
                let inst = el.querySelector('.instructions .inner') || el.querySelector('.instructions') || el;
                let clone = inst.cloneNode(true);

                // Remover elementos innecesarios
                clone.querySelectorAll('button, .copy-code-button, style, script, .devsite-banner').forEach(e => e.remove());

                return clone.innerHTML;
            }''')

            steps_data.append({
                "step_number": idx + 1,
                "label": label,
                "html": step_html
            })
            print(f"Paso {idx + 1}: '{label}' extraído ({len(step_html)} chars)")

        await browser.close()

        data = {
            "title": main_title,
            "updated_date": updated_date,
            "author": author,
            "source_url": url,
            "steps": steps_data
        }

        with open("scraped_codelab.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print("Scraping completado y guardado en scraped_codelab.json")

if __name__ == "__main__":
    asyncio.run(scrape_codelab())
