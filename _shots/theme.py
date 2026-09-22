import asyncio, os
from playwright.async_api import async_playwright

OUT="/home/user/prototype/_shots"

async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(viewport={"width":1600,"height":1000})
        errs=[]
        pg.on("console", lambda m: errs.append((m.type,m.text)) if m.type in ("error","warning") else None)
        pg.on("pageerror", lambda e: errs.append(("pageerror",str(e))))
        await pg.goto("file:///home/user/prototype/index.html")
        await pg.wait_for_timeout(800)

        # анимации: до прокрутки часть блоков скрыта, после — появляется
        before=await pg.evaluate("() => ({hidden: document.querySelectorAll('#scr-home .rv:not(.is-in)').length, rv: document.querySelectorAll('#scr-home .rv').length})")
        print("reveal до прокрутки:", before)

        # тёмная тема
        await pg.click('#scr-home .hd [data-theme-tgl]')
        await pg.wait_for_timeout(400)
        print("класс темы:", await pg.evaluate("() => document.getElementById('site').className"))
        print("подпись кнопки:", await pg.inner_text('#scr-home .hd [data-theme-tgl]'))
        await pg.screenshot(path=f"{OUT}/t1-dark-top.png")

        # прокрутка: липкая сжатая шапка
        await pg.evaluate("window.scrollTo(0,1400)")
        await pg.wait_for_timeout(900)
        print("sticky:", await pg.evaluate("() => {var hd=document.querySelector('#scr-home .hd'); return {cls:hd.className, top:getComputedStyle(hd).position, stickyTop:getComputedStyle(hd).top};}"))
        await pg.screenshot(path=f"{OUT}/t2-dark-sticky.png")

        # блок «видео и подкасты» + опрос в тёмной теме
        await pg.evaluate("() => document.getElementById('media').scrollIntoView({block:'start'})")
        await pg.wait_for_timeout(900)
        await pg.screenshot(path=f"{OUT}/t3-dark-media.png")

        # опрос: клик
        await pg.click('#poll .poll__o')
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path=f"{OUT}/t4-dark-poll.png")

        # «Для вас»: смена интереса
        await pg.evaluate("() => document.getElementById('foryou').scrollIntoView({block:'center'})")
        await pg.wait_for_timeout(700)
        await pg.click('#fyou .fyou__chip >> nth=2')
        await pg.wait_for_timeout(400)
        await pg.screenshot(path=f"{OUT}/t5-dark-foryou.png")

        # статья в тёмной теме + прогресс чтения
        await pg.click('#tabs .tab[data-scr="article"]')
        await pg.wait_for_timeout(600)
        await pg.evaluate("window.scrollTo(0,900)")
        await pg.wait_for_timeout(900)
        print("прогресс:", await pg.inner_text('#scr-article .progress'))
        await pg.screenshot(path=f"{OUT}/t6-dark-article.png")

        # светлая тема, статья: проверка прогресса
        await pg.click('#scr-article .hd [data-theme-tgl]')
        await pg.wait_for_timeout(400)
        await pg.evaluate("window.scrollTo(0,2600)")
        await pg.wait_for_timeout(900)
        print("прогресс светлая:", await pg.inner_text('#scr-article .progress'))
        await pg.screenshot(path=f"{OUT}/t7-light-article.png")

        # живая лента: добавление записи
        await pg.click('#tabs .tab[data-scr="home"]')
        await pg.wait_for_timeout(500)
        n0=await pg.locator('#livlist li').count()
        await pg.wait_for_timeout(12000)
        n1=await pg.locator('#livlist li').count()
        print("лента обновлений:", n0, "->", n1, "| первая запись:", (await pg.locator('#livlist li').first.inner_text()).replace("\n"," / ")[:90])
        print("ошибки:", errs or "нет")
        await b.close()

asyncio.run(main())
