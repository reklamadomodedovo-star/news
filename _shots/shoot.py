import asyncio, os
from playwright.async_api import async_playwright

OUT = "/home/user/prototype/_shots"
os.makedirs(OUT, exist_ok=True)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
        errs = []
        pg.on("console", lambda m: errs.append((m.type, m.text)) if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errs.append(("pageerror", str(e))))
        await pg.goto("file:///home/user/prototype/index.html")
        await pg.wait_for_timeout(900)
        await pg.add_style_tag(content=".top{position:static!important}.hd{position:static!important}"
            ".rv{opacity:1!important;translate:none!important;transition:none!important}"
            ".ticker__track{animation:none!important}")
        await pg.evaluate("""() => { document.querySelectorAll('[data-to]').forEach(function(el){ var v=+el.getAttribute('data-to'); el.setAttribute('data-c','1'); el.textContent=String(v).replace(/\\B(?=(\\d{3})+(?!\\d))/g,' '); }); }""")

        # диагностика
        diag = await pg.evaluate("""() => ({
            leftoverIcons: document.querySelectorAll('[data-ic]').length,
            drawnIcons: document.querySelectorAll('svg.ic').length,
            events: document.querySelectorAll('#evfeed .ev').length,
            evlist: document.querySelectorAll('#evlist .ev').length,
            calDays: document.querySelectorAll('#scr-calendar .cal__d').length,
            headers: document.querySelectorAll(".mast__in").length,
            footers: document.querySelectorAll('.ft__g').length,
            siteW: document.querySelector('#site').getBoundingClientRect().width,
        })""")
        print("DIAG", diag)

        # главная, desktop
        await pg.locator("#scr-home").screenshot(path=f"{OUT}/01-home-desktop.png")
        # главная с разметкой рекламы
        await pg.click("#chk-ads")
        await pg.locator("#scr-home").screenshot(path=f"{OUT}/02-home-ads.png")
        await pg.click("#chk-ads")

        # статья
        await pg.click('#tabs .tab[data-scr="article"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-article").screenshot(path=f"{OUT}/03-article-desktop.png")

        # календарь + клик по дню с событием
        await pg.click('#tabs .tab[data-scr="calendar"]')
        await pg.wait_for_timeout(300)
        await pg.locator('#scr-calendar [data-cal="page"]').get_by_role("button", name="26 сентябрь").click()
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-calendar").screenshot(path=f"{OUT}/04-calendar-desktop.png")

        # каталог
        await pg.click('#tabs .tab[data-scr="catalog"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-catalog").screenshot(path=f"{OUT}/05-catalog-desktop.png")

        # админка
        await pg.click('#tabs .tab[data-scr="admin"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-admin").screenshot(path=f"{OUT}/06-admin-desktop.png")

        # UI-кит
        await pg.click('#tabs .tab[data-scr="ui"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-ui").screenshot(path=f"{OUT}/07-ui-desktop.png")

        # WP
        await pg.click('#tabs .tab[data-scr="wp"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-wp").screenshot(path=f"{OUT}/08-wp-desktop.png")

        # мобильная главная
        await pg.click('#tabs .tab[data-scr="home"]')
        await pg.click('#dev .seg__b[data-w="390"]')
        await pg.wait_for_timeout(400)
        await pg.locator("#scr-home").screenshot(path=f"{OUT}/09-home-mobile.png")
        # мобильное меню
        await pg.click("#scr-home [data-burger]")
        await pg.wait_for_timeout(250)
        await pg.locator("#scr-home .hd").screenshot(path=f"{OUT}/10-home-mobile-menu.png")
        await pg.click("#scr-home [data-burger]")

        # мобильная статья + разметка рекламы
        await pg.click('#tabs .tab[data-scr="article"]')
        await pg.click("#chk-ads")
        await pg.wait_for_timeout(400)
        await pg.locator("#scr-article").screenshot(path=f"{OUT}/11-article-mobile-ads.png")
        await pg.click("#chk-ads")

        # мобильный календарь
        await pg.click('#tabs .tab[data-scr="calendar"]')
        await pg.wait_for_timeout(300)
        await pg.locator("#scr-calendar").screenshot(path=f"{OUT}/12-calendar-mobile.png")

        # планшет
        await pg.click('#dev .seg__b[data-w="834"]')
        await pg.click('#tabs .tab[data-scr="home"]')
        await pg.wait_for_timeout(400)
        await pg.locator("#scr-home").screenshot(path=f"{OUT}/13-home-tablet.png")

        print("CONSOLE:", errs[:15])
        print("scale check", await pg.evaluate("document.getElementById('device').style.transform"))
        await b.close()

asyncio.run(main())
