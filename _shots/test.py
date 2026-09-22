import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1400, "height": 950})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file:///home/user/prototype/index.html")
        await pg.wait_for_timeout(700)

        # 1. Подробности события на главной
        await pg.locator('#evfeed .ev').first.get_by_role("button", name="Подробнее").click()
        await pg.wait_for_timeout(200)
        det = await pg.locator('#evfeed .ev').first.locator('.detail').bounding_box()
        print("1) Детали события открылись, высота:", round(det['height']) if det else None)

        # 2. Напоминание
        await pg.locator('#evfeed .ev').first.get_by_role("button", name="Напомнить").click()
        print("2) Кнопка напоминания:", (await pg.locator('#evfeed .ev').first.locator('.rem-txt').inner_text()))

        # 3. Фильтры календаря
        await pg.click('#tabs .tab[data-scr="calendar"]')
        await pg.wait_for_timeout(200)
        await pg.locator('#scr-calendar .fchip').filter(has_text="Музыка").first.click()
        await pg.wait_for_timeout(150)
        n1 = await pg.locator('#evlist .ev').count()
        await pg.locator('#scr-calendar .fchip').filter(has_text="Бесплатно").first.click()
        await pg.wait_for_timeout(150)
        n2 = await pg.locator('#evlist .ev').count()
        txt = await pg.locator('#evcount').inner_text()
        print("3) Фильтр «Музыка»:", n1, "| + «Бесплатно»:", n2, "|", txt.replace("\n", " "))
        # сброс
        await pg.locator('#scr-calendar .fchip').filter(has_text="Все").first.click()
        await pg.locator('#scr-calendar .fchip').filter(has_text="Вся страна").first.click()
        await pg.locator('#scr-calendar .fchip').filter(has_text="Бесплатно").first.click()
        await pg.wait_for_timeout(150)
        print("   после сброса:", await pg.locator('#evlist .ev').count())

        # 4. Горизонтальный оверфлоу на каждом экране (телефон / планшет / ПК)
        for w in (390, 834, 1280):
            await pg.click(f'#dev .seg__b[data-w="{w}"]')
            for scr in ("home", "article", "calendar", "catalog", "admin", "ui", "wp", "check"):
                await pg.click(f'#tabs .tab[data-scr="{scr}"]')
                await pg.wait_for_timeout(120)
                r = await pg.evaluate("""() => {
                    const site=document.getElementById('site');
                    const over=[...site.querySelectorAll('*')].filter(el=>{
                      const b=el.getBoundingClientRect();
                      return b.width>0 && (b.right > site.getBoundingClientRect().right+2);
                    }).slice(0,4).map(el=>el.className||el.tagName);
                    return {scroll:site.scrollWidth, client:site.clientWidth, over};
                }""")
                bad = r['scroll'] > r['client'] + 2
                print(f"4) {w}px {scr}: overflow={'ДА '+str(r['over']) if bad else 'нет'}")

        # 5. Высота рекламных блоков на телефоне
        await pg.click('#dev .seg__b[data-w="390"]')
        await pg.click("#chk-ads")
        for scr in ("home", "article", "calendar", "catalog"):
            await pg.click(f'#tabs .tab[data-scr="{scr}"]')
            await pg.wait_for_timeout(150)
            h = await pg.evaluate("""() => [...document.querySelectorAll('.screen.is-on .ad')]
                .map(a=>Math.round(a.getBoundingClientRect().width)+'x'+Math.round(a.getBoundingClientRect().height))""")
            print(f"5) Реклама на телефоне, {scr}:", h)
        await pg.click("#chk-ads")

        # 6. Аккордеон «Подробнее» в списке календаря + .ics
        await pg.click('#tabs .tab[data-scr="calendar"]')
        await pg.wait_for_timeout(200)
        await pg.locator('#evlist .ev').first.get_by_role("button", name="Подробнее").click()
        await pg.wait_for_timeout(200)
        d2 = await pg.locator('#evlist .ev').first.locator('.detail').bounding_box()
        print("6) Аккордеон в календаре:", bool(d2), round(d2['height']) if d2 else None)
        async with pg.expect_download() as dl:
            await pg.locator('#evlist .ev').first.get_by_role("button", name="В календарь").click()
        d = await dl.value
        print("    .ics скачан:", d.suggested_filename)

        # 7. Подписка
        await pg.click('#tabs .tab[data-scr="home"]')
        await pg.wait_for_timeout(200)
        await pg.fill('#sub1', 'test@example.com')
        await pg.locator('#sub1').press('Enter')
        await pg.wait_for_timeout(300)
        print("7) Форма подписки:", await pg.locator('#scr-home .form-ok').inner_text())

        print("Ошибки JS:", errs or "нет")
        await b.close()

asyncio.run(main())
