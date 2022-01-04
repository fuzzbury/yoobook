import asyncio
import pyppeteer
from pyppeteer import launch

FILE = 'file:///C:/Users/JohnGay/AppData/Local/YooBook/YooBook/Documents/Contents/9789813288904/assets/gjn45gp53cn1588566608888/gjn45gp53cn158856660888810.html'


async def main():
    browser = await launch(defaultViewport=None)
    page = await browser.newPage()
    await page.goto(FILE)
    await page.emulateMedia('print');
    await page.screenshot({'path': r'c:\temp\example.png'})
    await page.pdf(path=r'c:\temp\example.pdf', pageRanges='1', printBackground=True, format="a4",
                   displayHeaderFooter=True, headerTemplate='html', )

    await browser.close()

print(pyppeteer.version_info)
asyncio.get_event_loop().run_until_complete(main())
