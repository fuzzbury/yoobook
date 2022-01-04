import sys
import os
import pdfkit
import re
import asyncio
from pyppeteer import launch
from tqdm import tqdm
from PyPDF2 import PdfFileMerger
import json

BOOKS = {
    'ConquerMathematics6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813288768',
    'ConquerMathematics5': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813288904',
    'LearningMathematics6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813321823',
    'ConquerExamStandardMathematicsProblemSums6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813285187',
    'E-LearningEnglishVocabularyWorkbook6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813284074',
    'E-ConquerEnglishSynthesisAndTransformationWorkbook6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789813285453',
    'E-ConquerComprehensionWorkbook6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789814438162',
    'E-101ChallengingMathsWordProblemsBook6': r'%localappdata%\YooBook\YooBook\Documents\Contents\9789814438759',
}

BOOK_NAME = 'E-101ChallengingMathsWordProblemsBook6'
TEMP_FOLDER = r'c:\temp'

book_folder = os.path.expandvars(BOOKS[BOOK_NAME])


async def main():
    browser = await launch()
    page = await browser.newPage()

    with open(os.path.join(book_folder, 'contents.js'), 'r') as f:
        contents = f.read()
        contents = contents.replace('var bookData =', '')
        contents_dicts = json.loads(contents)

    normal_page_pattern = r'<iframe src="assets/(\w*)/(\w*).html"'
    cover_page_pattern = r'<img id="img-id-\w*" class="img-responsive pull-center\s*?" style="width:100%;" src="images/\w*.jpeg" data-retina retina-support="false">'

    html_files = []
    for dico in contents_dicts:
        html_files.append((os.path.join(book_folder, f'{dico["PID"]}.html'), dico["Title"]))

    temp_files = []
    i_page = 1
    for (full_path, bookmark) in tqdm(html_files):
        print(f'processing {full_path}')
        with open(full_path, 'r') as f:
            text = f.read()
            matches = re.search(normal_page_pattern, text)
            target = None
            if matches:
                target = os.path.join(book_folder, 'assets', matches[1], f'{matches[2]}.html')
            else:
                matches = re.search(cover_page_pattern, text)
                if matches:
                    target = full_path

            if target:
                print(f'saving page {i_page}: {target}')
                await page.goto(target)
                temp_file = os.path.join(TEMP_FOLDER, fr'{BOOK_NAME}_{i_page:04}.pdf')
                temp_files.append((temp_file, bookmark))
                await page.pdf(path=temp_file, pageRanges='1')
                i_page += 1

    # now merge and delete other temp files

    merger = PdfFileMerger()

    for (pdf, bookmark) in temp_files:
        print(f'merging {pdf}')
        merger.append(pdf, bookmark=bookmark)

    save_file = os.path.join(TEMP_FOLDER, fr'{BOOK_NAME}.pdf')
    with open(save_file, "wb") as fout:
        merger.write(fout)
        print(f'saved to {save_file}')
    merger.close()

    print('deleting intermediate files..')
    for (pdf, bookmark) in temp_files:
        os.remove(pdf)
    print('intermediate files deleted')
    print(f'FINISHED, BOOK HERE {save_file}')


asyncio.get_event_loop().run_until_complete(main())
