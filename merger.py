import enum

from pypdf import PdfWriter, PdfReader


class BookmarkMode(enum.Enum):
    NO_BOOKMARK = 0
    # source file names are used as output bookmarks
    FILE_NAME_AS_BOOKMARK = 1
    # source file names and bookmark are used as output bookmarks
    FILE_NAME_AND_SECTION_AS_BOOKMARK = 2

def combine_pdf_files(source_files: list[str], output_file: str, bookmark_mode: BookmarkMode, tick_callback):
    """
    Combine multiple PDF files into one.
    :param source_files: list of source PDF file paths
    :param output_file: output PDF file path
    :param bookmark_mode: BookmarkMode.FILE_NAME_AND_SECTION_AS_BOOKMARK is commonly used.
    :param tick_callback: a callback function to be called after each file is processed. Set it to None if not needed.
    :return: None
    """
    merger = PdfWriter()
    page_num = 0

    def insert_bookmarks(reader, bookmark_or_list, parent, last_added_bm=None):
        # last_added_bm = parent
        if isinstance(bookmark_or_list, list):
            for bm in bookmark_or_list:
                if isinstance(bm, list):
                    insert_bookmarks(reader, bm, last_added_bm)
                else:
                    last_added_bm = insert_bookmarks(reader, bm, parent)
        else:
            item = bookmark_or_list
            page_offset = reader.get_destination_page_number(item)
            # print(f"{item.title} => {page_offset}")
            return merger.add_outline_item(item.title, page_num + page_offset, parent)

    for file_path in source_files:
        file_name = file_path.split('/')[-1]

        # trim off the .pdf extension
        if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
            file_name = file_name[:-4]

        with open(file_path, 'rb') as pdf_file:
            if tick_callback is not None:
                tick_callback()
            pdf_reader = PdfReader(pdf_file)
            merger.append_pages_from_reader(pdf_reader)
            new_outline = merger.add_outline_item(file_name, page_num)
            insert_bookmarks(pdf_reader, pdf_reader.outline, new_outline)
            page_num += len(pdf_reader.pages)

    merger.write(output_file)
    merger.close()
