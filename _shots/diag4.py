import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={"width":1400,"height":950})
        await pg.goto("file:///home/user/prototype/index.html"); await pg.wait_for_timeout(400)
        for w in (390,):
            await pg.click(f'#dev .seg__b[data-w="{w}"]')
            for scr in ("admin","catalog","ui","wp","check","calendar"):
                await pg.click(f'#tabs .tab[data-scr="{scr}"]'); await pg.wait_for_timeout(250)
                r=await pg.evaluate("""() => {
                  const site=document.getElementById('site'); const sr=site.getBoundingClientRect(); const out=[];
                  site.querySelectorAll('*').forEach(el=>{
                    const b=el.getBoundingClientRect();
                    if(b.width>0 && b.right>sr.right+1){
                      let par=el.parentElement, clipped=false;
                      while(par && par!==site){const cs=getComputedStyle(par); if(cs.overflowX!=='visible'){clipped=true;break;} par=par.parentElement;}
                      if(!clipped) out.push({cls:(el.className&&el.className.baseVal!==undefined?el.className.baseVal:el.className)||el.tagName, w:Math.round(b.width), over:Math.round(b.right-sr.right), txt:(el.textContent||'').trim().slice(0,30)});
                    }});
                  return {scroll:site.scrollWidth, client:site.clientWidth, out:out.slice(0,8)};
                }""")
                print(f"--- {scr} 390px: scroll={r['scroll']} client={r['client']}")
                for o in r['out']: print("    ", o)
        await b.close()
asyncio.run(main())
