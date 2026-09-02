import asyncio
import json
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

MODULE_DEFINITIONS = [
    {
        "id": "modulo_1",
        "title": "Módulo 1: Introducción y Primeros Pasos en Google Cloud",
        "pdf_filename": "Modulo_1_Introduccion_y_Primeros_Pasos.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs?hl=es-419",
            "https://docs.cloud.google.com/docs/overview?hl=es-419",
            "https://docs.cloud.google.com/docs/get-started?hl=es-419",
            "https://docs.cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison?hl=es-419",
            "https://docs.cloud.google.com/docs/enterprise/cloud-setup?hl=es-419",
            "https://docs.cloud.google.com/docs/authentication?hl=es-419",
            "https://docs.cloud.google.com/docs/quotas?hl=es-419"
        ]
    },
    {
        "id": "modulo_2",
        "title": "Módulo 2: Inteligencia Artificial y Aprendizaje Automático",
        "pdf_filename": "Modulo_2_IA_y_Aprendizaje_Automatico.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/ai-ml?hl=es-419",
            "https://docs.cloud.google.com/docs/generative-ai?hl=es-419",
            "https://docs.cloud.google.com/docs/ai-ml/generative-ai?hl=es-419"
        ]
    },
    {
        "id": "modulo_3",
        "title": "Módulo 3: Desarrollo y Hosting de Aplicaciones",
        "pdf_filename": "Modulo_3_Desarrollo_y_Hosting_de_Aplicaciones.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/application-development?hl=es-419",
            "https://docs.cloud.google.com/docs/application-hosting?hl=es-419",
            "https://docs.cloud.google.com/docs/devtools?hl=es-419",
            "https://docs.cloud.google.com/docs/buildpacks?hl=es-419",
            "https://docs.cloud.google.com/docs/gitlab?hl=es-419",
            "https://docs.cloud.google.com/docs/samples?hl=es-419"
        ]
    },
    {
        "id": "modulo_4",
        "title": "Módulo 4: Procesamiento y Almacenamiento",
        "pdf_filename": "Modulo_4_Procesamiento_y_Almacenamiento.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/compute-area?hl=es-419",
            "https://docs.cloud.google.com/docs/storage?hl=es-419"
        ]
    },
    {
        "id": "modulo_5",
        "title": "Módulo 5: Bases de Datos y Análisis de Datos",
        "pdf_filename": "Modulo_5_Bases_de_Datos_y_Analisis_de_Datos.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/databases?hl=es-419",
            "https://docs.cloud.google.com/docs/data?hl=es-419"
        ]
    },
    {
        "id": "modulo_6",
        "title": "Módulo 6: Redes, Seguridad y Gestión de Accesos",
        "pdf_filename": "Modulo_6_Redes_y_Seguridad.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/networking?hl=es-419",
            "https://docs.cloud.google.com/docs/security?hl=es-419",
            "https://docs.cloud.google.com/docs/security/overview/whitepaper?hl=es-419",
            "https://docs.cloud.google.com/docs/access-resources?hl=es-419"
        ]
    },
    {
        "id": "modulo_7",
        "title": "Módulo 7: Infraestructura, Observabilidad, Migración y Costos",
        "pdf_filename": "Modulo_7_Infraestructura_Observabilidad_y_Migracion.pdf",
        "urls": [
            "https://docs.cloud.google.com/docs/iac?hl=es-419",
            "https://docs.cloud.google.com/docs/terraform?hl=es-419",
            "https://docs.cloud.google.com/docs/observability?hl=es-419",
            "https://docs.cloud.google.com/docs/migration?hl=es-419",
            "https://docs.cloud.google.com/docs/dhm-cloud?hl=es-419",
            "https://docs.cloud.google.com/docs/costs-usage?hl=es-419",
            "https://docs.cloud.google.com/docs/cuds?hl=es-419",
            "https://docs.cloud.google.com/docs/industry?hl=es-419",
            "https://docs.cloud.google.com/docs/cross-product-overviews?hl=es-419",
            "https://docs.cloud.google.com/docs/product-list?hl=es-419",
            "https://docs.cloud.google.com/docs/whats-new?hl=es-419"
        ]
    }
]

async def extract_page_content(page, url):
    logging.info(f"Navegando a: {url}")
    try:
        response = await page.goto(url, wait_until="networkidle", timeout=45000)
        if not response or response.status >= 400:
            logging.warning(f"Error HTTP {response.status if response else 'No Response'} al acceder a {url}")
    except Exception as e:
        logging.error(f"Error cargando {url}: {e}")

    # Extract clean content
    data = await page.evaluate('''() => {
        let titleEl = document.querySelector('h1') || document.querySelector('title');
        let title = titleEl ? titleEl.innerText.trim() : document.title;

        // Devsite main article container
        let article = document.querySelector('.devsite-article-body') ||
                      document.querySelector('devsite-content') ||
                      document.querySelector('article') ||
                      document.querySelector('main');

        if (!article) {
            return { title: title, html: "<p>No se pudo extraer el contenido de esta sección.</p>" };
        }

        let clone = article.cloneNode(true);

        // Clean unwanted elements (nav, breadcrumbs, banners, buttons, feedback, sidebars)
        let selectorToRemove = [
            'devsite-header', 'devsite-footer', 'devsite-sidebar', 'devsite-breadcrumb',
            'devsite-bookmark', 'devsite-content-footer', '.devsite-feedback',
            '.devsite-article-meta', 'button', '.copy-code-button', 'style', 'script',
            'devsite-subpage-nav', 'devsite-toc', 'devsite-page-rating'
        ].join(',');

        clone.querySelectorAll(selectorToRemove).forEach(e => e.remove());

        // Process images - fix relative URLs
        clone.querySelectorAll('img').forEach(img => {
            let src = img.getAttribute('src');
            if (src) {
                if (src.startsWith('//')) {
                    img.setAttribute('src', 'https:' + src);
                } else if (src.startsWith('/')) {
                    img.setAttribute('src', 'https://docs.cloud.google.com' + src);
                }
            }
        });

        // Process links - fix relative URLs
        clone.querySelectorAll('a').forEach(a => {
            let href = a.getAttribute('href');
            if (href) {
                if (href.startsWith('/')) {
                    a.setAttribute('href', 'https://docs.cloud.google.com' + href);
                }
            }
        });

        return {
            title: title,
            html: clone.innerHTML
        };
    }''')

    return {
        "url": url,
        "page_title": data.get("title", ""),
        "html": data.get("html", "")
    }

async def scrape_all_docs():
    modules_output = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for mod_def in MODULE_DEFINITIONS:
            logging.info(f"=== Procesando {mod_def['title']} ===")
            scraped_pages = []

            for url in mod_def["urls"]:
                page_data = await extract_page_content(page, url)
                scraped_pages.append(page_data)
                await asyncio.sleep(0.5)

            modules_output.append({
                "id": mod_def["id"],
                "title": mod_def["title"],
                "pdf_filename": mod_def["pdf_filename"],
                "pages": scraped_pages
            })

        await browser.close()

    with open("gcp_docs_data.json", "w", encoding="utf-8") as f:
        json.dump(modules_output, f, ensure_ascii=False, indent=2)

    logging.info("Scraping completado con éxito. Archivo gcp_docs_data.json guardado.")

if __name__ == "__main__":
    asyncio.run(scrape_all_docs())
