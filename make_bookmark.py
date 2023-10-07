# This program read a PDF file and make bookmarks for it.
# The bookmarks are specified in a json file.
# The json file is a list of items, each item has two required keys:
#   "title": the title of the bookmark
#   "page": the page number of the bookmark
# Each item may have an optional key:
#   "children": a list of items, each item is a child of the current item
#   and has the same structure.

import sys
import json
from pypdf import PdfReader, PdfWriter


class Bookmark:
    def __init__(self, title: str, page: int, children: list | None):
        self.title = title
        self.page = page
        self.children = children

    def __str__(self):
        return f"{self.title} on page {self.page}"


def json_to_bookmarks(json_obj) -> list[Bookmark]:
    bookmarks: list[Bookmark] = []
    for item in json_obj:
        title = item["title"]
        page = item["page"]
        if "children" in item:
            children_obj = item["children"]
            children = json_to_bookmarks(children_obj)
            bookmark = Bookmark(title, page, children)
        else:
            bookmark = Bookmark(title, page, None)

        bookmarks.append(bookmark)
    return bookmarks

def insert_bookmarks(writer, bookmarks: list[Bookmark], parent=None):
    for bookmark in bookmarks:
        # "page" is 1-based, but "add_outline_item" requires 0-based page number
        new_outline = writer.add_outline_item(bookmark.title, bookmark.page - 1, parent)
        if bookmark.children is not None:
            insert_bookmarks(writer, bookmark.children, new_outline)

def make_bookmark(source_path: str, json_path: str, output_path: str):
    with open(json_path, "rb") as f_json:
        json_obj = json.load(f_json)
        bookmarks = json_to_bookmarks(json_obj)

    pdf_reader = PdfReader(source_path)
    pdf_writer = PdfWriter()

    pdf_writer.append_pages_from_reader(pdf_reader)
    insert_bookmarks(pdf_writer, bookmarks)

    pdf_writer.write(output_path)
    pdf_writer.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: make_bookmark.py source.pdf bookmark.json output.pdf")
        sys.exit(1)

    src_path = sys.argv[1]
    j_path = sys.argv[2]
    dst_path = sys.argv[3]

    make_bookmark(src_path, j_path, dst_path)