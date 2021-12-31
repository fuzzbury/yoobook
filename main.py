import sys
import os
import pdfkit
import re
import asyncio
from pyppeteer import launch
from tqdm import tqdm
from PyPDF2 import PdfFileMerger

# note have just discovered the file contents.js
# which has the paged in order
# that would be the better way to find the pages


# rundll32.exe %windir%\system32\mshtml.dll,PrintHTML "C:\Users\JohnGay\AppData\Local\YooBook\YooBook\Documents\Contents\9789813321823\assets\y9bttxij4sc1615703900755\y9bttxij4sc161570390075534.html"

BOOK_NAME = 'ConquerMathematics6'
# BOOK_FOLDER =  r'C:\Users\JohnGay\AppData\Local\YooBook\YooBook\Documents\Contents\9789813288904'
# BOOK_FOLDER = r'C:\Users\JohnGay\AppData\Local\YooBook\YooBook\Documents\Contents\9789813321823'
# BOOK_FOLDER = r'C:\Users\JohnGay\AppData\Local\YooBook\YooBook\Documents\Contents\9789813285187'
BOOK_FOLDER = r'C:\Users\JohnGay\AppData\Local\YooBook\YooBook\Documents\Contents\9789813288768'
TEMP_FOLDER = r'c:\temp'


async def main():
    browser = await launch()
    page = await browser.newPage()

    pattern = r'<iframe src="assets/(\w*)/(\w*).html"'
    main_page_pattern = r'<img id="img-id-\w*" class="img-responsive pull-center\s*?" style="width:100%;" src="images/\w*.jpeg" data-retina retina-support="false">'

    html_files = []
    for file in os.listdir(BOOK_FOLDER):
        if file.endswith('.html'):
            full_path = os.path.join(BOOK_FOLDER, file)
            html_files.append((full_path, os.path.getmtime(full_path)))

    ordered_html_files = [x[0] for x in sorted(html_files, key=lambda z: z[0], reverse=False)]

    temp_files = []
    i_page = 1
    for full_path in tqdm(ordered_html_files):
        print(f'processing {full_path}')
        with open(full_path, 'r') as f:
            text = f.read()
            matches = re.search(pattern, text)
            target = None
            if matches:
                target = os.path.join(BOOK_FOLDER, 'assets', matches[1], f'{matches[2]}.html')
            else:
                matches = re.search(main_page_pattern, text)
                if matches:
                    target = full_path

            if target:
                print(f'saving page {i_page}: {target}')
                await page.goto(target)
                temp_file = os.path.join(TEMP_FOLDER, fr'{BOOK_NAME}_{i_page:04}.pdf')
                temp_files.append(temp_file)
                await page.pdf(path=temp_file, pageRanges='1')
                i_page += 1

    # now merge and delete other temp files

    merger = PdfFileMerger()

    for pdf in temp_files:
        print(f'merging {pdf}')
        merger.append(pdf, 'rb')

    save_file = os.path.join(TEMP_FOLDER, fr'{BOOK_NAME}.pdf')
    with open(save_file, "wb") as fout:
        merger.write(fout)
        print(f'saved to {save_file}')
    merger.close()

    print('deleting intermediate files..')
    for pdf in temp_files:
        os.remove(pdf)
    print('intermediate files deleted')
    print(f'FINISHED, BOOK HERE {save_file}')


asyncio.get_event_loop().run_until_complete(main())
