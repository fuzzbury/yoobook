import sys
import os
import pdfkit
import re
import asyncio
from pyppeteer import launch
from tqdm import tqdm
from PyPDF2 import PdfFileMerger
import json
import book_name
from pathlib import Path
import tempfile

BOOK_NAME = 'ALL'  # ALL o None for everything
TEMP_FOLDER = r'c:\temp'

YOU_BOOK_PATH = '%localappdata%\YooBook\YooBook\Documents\Contents'

BOOKS = {
    'MathOlympiadSecondary3&4': r'9789813323896',
    'e-MathsOlympiad-Advanced': r'9789813283299',
    'MathOlympiadPrimary5&6': r'9789813323872',
    'e-MathsOlympiad–UnleashTheMathsOlympianInYou-TheNextLap': r'9789813283305',
    'MathOlympiadSecondary1&2': r'9789813323889',

    'ConquerMathematics6': r'9789813288768',
    'ConquerMathematics5': r'9789813288904',
    'LearningMathematics6': r'9789813321823',
    'e-ConquerExam-StandardMathematicsProblemSums-Primary6': r'9789813285187',
    'e-LearningEnglishVocabularyWorkbook6': r'9789813284074',
    'e-ConquerEnglishSynthesisAndTransformationWorkbook6': r'9789813285453',
    'E-ConquerComprehensionWorkbook6': r'9789814438162',
    'e-101 Challenging Maths Word Problems Book 6': '9789814438759',

    'e-Strengthen English Editing For Lower Secondary Levels': '9789813218932',
    'e-Strengthen English Visual Text Comprehension For Lower Secondary Levels': '9789813218987',
    'e-Integrated Mathematics Numbers, Graphs And Statistics for Secondary 1': '9789813285026',
    'e-Vocabulary Builder Secondary Level 1': '9789813285361',
    'e-Integrated Mathematics Algebra for Secondary 1': '9789813286603',
    'e-Strengthen English Vocabulary For Secondary Levels': '9789813286610',
    'e-Mathematics Problem-S olving In Real World Contexts For Lower Secondary Levels': '9789813286924',
    'e-Strengthen English Grammar For Secondary Levels': '9789813289055',
    'e-Integrated Mathematics Geometry And Mensuration for Secondary 1': '9789813321625',
    'e-Conquer Mathematics Secondary 1': '9789813323216',
    'e-Strengthen English Idioms For Secondary Levels': '9789813323933',
    'e-Strengthen English For Phrasal Verbs Secondary Levels': '9789813324077',

}


async def extract_book(book_folder, write_folder):
    browser = await launch()
    page = await browser.newPage()

    with open(os.path.join(book_folder, 'contents.js'), 'r', encoding="utf8") as f:
        contents = f.read()
        contents = contents.replace('var bookData =', '')
        contents_dicts = json.loads(contents)

    normal_page_pattern = r'<iframe src="assets/(\w*)/(\w*).html"'
    cover_page_pattern = r'<img id="img-id-\w*" class="img-responsive pull-center\s*?" style="width:100%;" src="images/\w*.jpeg" data-retina retina-support="false">'

    html_files = []
    for dico in contents_dicts:
        html_files.append((os.path.join(book_folder, f'{dico["PID"]}.html'), dico["Title"]))

    with tempfile.TemporaryDirectory() as temp_dir:
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

                    id = Path(book_folder).name
                    name = id

                    # try to find the name from id
                    for k, v in BOOKS.items():
                        if v == id:
                            name = k
                            break

                    temp_file = os.path.join(temp_dir, fr'{name}_{i_page:04}.pdf')
                    temp_files.append((temp_file, bookmark))
                    await page.pdf(path=temp_file, pageRanges='1')
                    i_page += 1

        # now merge and delete other temp files

        merger = PdfFileMerger()

        for (pdf, bookmark) in temp_files:
            print(f'merging {pdf}')
            merger.append(pdf, bookmark=bookmark)

        save_file = os.path.join(write_folder, fr'{name}.pdf')
        with open(save_file, "wb") as fout:
            merger.write(fout)
            print(f'saved to {save_file}')
        merger.close()

        print('deleting intermediate files..')
        for (pdf, bookmark) in temp_files:
            os.remove(pdf)
        print('intermediate files deleted')
        print(f'FINISHED, BOOK HERE {save_file}')


if BOOK_NAME == 'ALL' or BOOK_NAME == None:
    # iterate the yoo books older and pass in all the child folders
    yoo_books_folder = Path(os.path.expandvars(YOU_BOOK_PATH))
    for x in yoo_books_folder.iterdir():
        # only take if a folder and like 9789813321823
        if x.is_dir() and re.match(r'\d{13}', x.name):
            asyncio.get_event_loop().run_until_complete(extract_book(x, TEMP_FOLDER))
else:
    book_folder = os.path.expandvars(os.path.join(YOU_BOOK_PATH, BOOKS[BOOK_NAME]))
    asyncio.get_event_loop().run_until_complete(extract_book(book_folder, TEMP_FOLDER))
