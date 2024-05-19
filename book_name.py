from bs4 import BeautifulSoup
from pathlib import Path


def make_valid_filename(input_string: str) -> str:
    # Define a list of illegal characters for Windows filenames
    illegal_chars = '<>:"/\\|?*'
    # Add the ASCII control characters
    illegal_chars += ''.join(chr(i) for i in range(32))

    # Remove invalid characters
    valid_filename = ''.join(c for c in input_string if c not in illegal_chars)
    # Replace spaces with underscores
    valid_filename = valid_filename.replace(' ', '_')
    return valid_filename


def get_soup(file: str) -> BeautifulSoup:
    with open(file, 'r') as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'html.parser')
    return soup


def get_first_div_after_img(soup: BeautifulSoup) -> str:
    img_tag = soup.find('img')
    if img_tag:
        div_tag = img_tag.find_next_sibling('div')
        if div_tag:
            return div_tag.get_text()
    return None


def get_book_file_name(file_contents_html: str) -> str:
    soup_contents = get_soup(file_contents_html)

    src_html = soup_contents.find('iframe')['src']
    full_src_html = Path(file_contents_html).parent / src_html

    soup_src = get_soup(full_src_html)

    book_name = get_first_div_after_img(soup_src)

    book_file_name = make_valid_filename(book_name)
    return book_file_name
