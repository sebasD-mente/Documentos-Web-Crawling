import asyncio
import json
from urllib.parse import urljoin
from playwright.async_api import async_playwright

MODULE_DEFINITIONS = [
    {
        "id": "modulo_1_guias_y_documentacion_general",
        "title": "Módulo 1: Guías y Documentación General",
        "urls": [
            "https://jules.google/docs/",
            "https://jules.google/docs/environment/",
            "https://jules.google/docs/running-tasks/",
            "https://jules.google/docs/scheduled-tasks/",
            "https://jules.google/docs/suggested-tasks/",
            "https://jules.google/docs/review-plan/",
            "https://jules.google/docs/code/",
            "https://jules.google/docs/tasks-repos/",
            "https://jules.google/docs/repo/",
            "https://jules.google/docs/errors/",
            "https://jules.google/docs/usage-limits/",
            "https://jules.google/docs/feedback/",
            "https://jules.google/docs/faq/",
            "https://jules.google/docs/contact/"
        ]
    },
    {
        "id": "modulo_2_referencia_rest_api",
        "title": "Módulo 2: Referencia de la REST API",
        "urls": [
            "https://jules.google/docs/api/reference/",
            "https://jules.google/docs/api/reference/overview",
            "https://jules.google/docs/api/reference/authentication",
            "https://jules.google/docs/api/reference/sessions",
            "https://jules.google/docs/api/reference/activities",
            "https://jules.google/docs/api/reference/sources",
            "https://jules.google/docs/api/reference/types"
        ]
    },
    {
        "id": "modulo_3_herramientas_cli",
        "title": "Módulo 3: Herramientas CLI de Jules (Jules Tools)",
        "urls": [
            "https://jules.google/docs/cli/reference",
            "https://jules.google/docs/cli/examples"
        ]
    },
    {
        "id": "modulo_4_guias_e_integraciones",
        "title": "Módulo 4: Guías e Integraciones",
        "urls": [
            "https://jules.google/docs/guides/continuous-ai-overview",
            "https://jules.google/docs/integrations/",
            "https://jules.google/docs/integrations/render"
        ]
    },
    {
        "id": "modulo_5_registro_de_cambios",
        "title": "Módulo 5: Registro de Cambios (Changelog)",
        "urls": [
            "https://jules.google/docs/changelog/"
        ]
    }
]

async def extract_page_content(page, url):
    await page.goto(url, wait_until="networkidle")

    data = await page.evaluate('''() => {
        let main = document.querySelector("main") || document.querySelector("article") || document.body;
        let clone = main.cloneNode(true);

        // Remove unwanted elements
        clone.querySelectorAll("footer, .pagination, header, nav, button, form, .sl-flex:not(.sl-markdown-content *)").forEach(el => el.remove());

        // Extract title
        let pageTitle = "";
        let h1 = clone.querySelector("h1") || document.querySelector("h1");
        if (h1) {
            pageTitle = h1.innerText.trim();
        } else {
            pageTitle = document.title.replace(" | Jules", "").trim();
        }

        // Clean internal links to keep text readable
        clone.querySelectorAll("a").forEach(a => {
            if (a.hostname === window.location.hostname) {
                // Ensure link has absolute URL or clean fragment
            }
        });

        // Ensure image URLs are absolute
        clone.querySelectorAll("img").forEach(img => {
            if (img.src) {
                img.src = img.src; // resolves to absolute
            }
        });

        return {
            title: pageTitle,
            html: clone.innerHTML
        };
    }''')

    return data

async def scrape_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # First crawl changelog to discover all changelog entries
        print("Obteniendo todas las entradas de Changelog...")
        await page.goto("https://jules.google/docs/changelog/", wait_until="networkidle")
        changelog_links = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll("a[href*='/docs/changelog/']"))
                .map(a => a.href.split('#')[0])
                .filter((v, i, self) => self.indexOf(v) === i && v !== "https://jules.google/docs/changelog/");
        }''')

        # Sort changelog links (they are usually dated, e.g. /2026-03-09)
        changelog_links.sort(reverse=True)
        print(f"Encontradas {len(changelog_links)} entradas de Changelog.")

        # Update Module 5 URLs with discovered entries
        for mod in MODULE_DEFINITIONS:
            if mod["id"] == "modulo_5_registro_de_cambios":
                mod["urls"].extend(changelog_links)

        results = []

        for mod in MODULE_DEFINITIONS:
            print(f"\n--- Procesando {mod['title']} ({len(mod['urls'])} páginas) ---")
            mod_data = {
                "id": mod["id"],
                "title": mod["title"],
                "pages": []
            }

            visited_urls = set()
            for url in mod["urls"]:
                clean_url = url.rstrip("/")
                if clean_url in visited_urls:
                    continue
                visited_urls.add(clean_url)

                try:
                    print(f"  Extrayendo: {url}")
                    page_content = await extract_page_content(page, url)
                    mod_data["pages"].append({
                        "url": url,
                        "title": page_content["title"],
                        "html": page_content["html"]
                    })
                except Exception as e:
                    print(f"  Error en {url}: {e}")

            results.append(mod_data)

        await browser.close()

        with open("scraped_jules_docs.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print("\n¡Scraping finalizado exitosamente! Datos guardados en scraped_jules_docs.json.")

if __name__ == "__main__":
    asyncio.run(scrape_all())
