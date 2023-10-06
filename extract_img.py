import sys

import pdfplumber

def extract_image(source_path: str, output_path):
    with pdfplumber.open(source_path) as pdf:
        num_pages = len(pdf.pages)
        for i in range(num_pages):
            page = pdf.pages[i]
            image = page.to_image()
            image.save(f'{output_path}/{i}.png', format='PNG')


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python extract_img.py source_path output_path')
        exit(1)
    source = sys.argv[1]
    output = sys.argv[2]
    extract_image(source, output)
