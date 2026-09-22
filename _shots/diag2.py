import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":1400,"height":950})
        await pg.goto("file:///home/user/prototype/index.html"); await pg.wait_for_timeout(500)
        await pg.click('#dev .seg__b[data-w="390"]'); await pg.wait_for_timeout(400)
        r=await pg.evaluate("""() => {
          const site=document.getElementById('site');
          const wrap=document.querySelector('#scr-home .wrap');
          const split=document.querySelector('#scr-home .split');
          const dev=document.getElementById('device');
          return {
            supports: CSS.supports('container-type: inline-size'),
            devW: dev.style.getPropertyValue('--dw'), devRect: Math.round(dev.getBoundingClientRect().width),
            siteW: Math.round(site.getBoundingClientRect().width),
            siteCS: getComputedStyle(site).containerType + ' / ' + getComputedStyle(site).containerName,
            wrapW: Math.round(wrap.getBoundingClientRect().width),
            wrapPad: getComputedStyle(wrap).paddingLeft,
            splitCols: getComputedStyle(split).gridTemplateColumns,
            h1size: getComputedStyle(document.querySelector('#scr-home h1')).fontSize,
            navDisp: getComputedStyle(document.querySelector('#scr-home .nav')).display,
          };
        }""")
        print(r)
        await b.close()
asyncio.run(main())
