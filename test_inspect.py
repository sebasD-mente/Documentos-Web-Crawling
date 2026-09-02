import asyncio

from playwright.async_api import async_playwright


async def inspect_categories():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(
            "https://docs.cloud.google.com/docs?hl=es-419",
            wait_until="networkidle",
        )

        categories = await page.evaluate("""() => {
            let results = [];
            let links = Array.from(document.querySelectorAll('a[href*="/docs"]'));
            links.forEach(a => {
                let href = a.href;
                let text = a.innerText.trim();
                if (href.includes('docs.cloud.google.com/docs') && text && !href.includes('#')) {
                    let urlObj = new URL(href);
                    urlObj.searchParams.set('hl', 'es-419');
                    results.push({ title: text.replace(/\\n/g, ' '), url: urlObj.toString() });
                }
            });
            return results;
        }""")

        unique_cats = {}
        for c in categories:
            url_path = c["url"].split("?")[0]
            if url_path not in unique_cats:
                unique_cats[url_path] = c

        print(f"Found {len(unique_cats)} category hubs:")
        for path, cat in unique_cats.items():
            print(f"  {cat['title']} -> {cat['url']}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(inspect_categories())
