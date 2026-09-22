import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1400,"height":950})
        await pg.goto("file:///home/user/prototype/index.html"); await pg.wait_for_timeout(500)
        for w in (834,390):
            await pg.click(f'#dev .seg__b[data-w="{w}"]'); await pg.wait_for_timeout(350)
            r=await pg.evaluate("""() => {
              const q=s=>document.querySelector(s);
              const f=e=>{const b=e.getBoundingClientRect();return {w:Math.round(b.width),l:Math.round(b.left),r:Math.round(b.right)};};
              const top=q('#scr-home .hd__top');
              return {w:innerWidth, site:f(q('#site')), wrap:f(q('#scr-home .wrap')), top:f(top), brand:f(q('#scr-home .brand')),
                search:f(q('#scr-home .hd__search')), searchIn:f(q('#scr-home .hd__search .search')), act:f(q('#scr-home .hd__act')),
                col1:f(q('#scr-home .split')), h1:f(q('#scr-home h1'))};
            }""")
            print(w, r)
        await b.close()
asyncio.run(main())
