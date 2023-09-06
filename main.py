import sys

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QAction, \
    QVBoxLayout, QFileDialog, QListWidget
from pypdf import PdfWriter, PdfReader


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("File Selection Example")
        self.setGeometry(100, 100, 600, 400)

        # Create a QListWidget to display selected filenames
        self.fileListWidget = QListWidget(self)

        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.fileListWidget)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self._setUpMenuBar()

    def _setUpMenuBar(self):
        # Set up menu bar
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        open_action = QAction("Add Files", self)
        open_action.triggered.connect(self.openFileDialog)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        # bind ctrl+q on Windows/Linux or cmd+q on Mac to exit
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        run_menu = menu.addMenu("Run")
        combine_action = QAction("Print List", self)
        combine_action.triggered.connect(self.combinePdfs)
        combine_action.setShortcut("Ctrl+R")
        run_menu.addAction(combine_action)

        help_menu = menu.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.openAboutDialog)
        help_menu.addAction(about_action)

    def openAboutDialog(self):
        QMessageBox.about(self, "About", "This is my awesome program.\n https://www.example.com")

    def openFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly  # You can add more options as needed

        # Display the file dialog and get selected file(s)
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        files, _ = file_dialog.getOpenFileNames(self, "Add File(s)", "", "PDF Files (*.pdf)", options=options)

        if files:
            # Add selected filenames to the QListWidget
            self.fileListWidget.addItems(files)

    def combinePdfs(self):
        length = self.fileListWidget.count()
        file_paths = [self.fileListWidget.item(i).text() for i in range(length)]
        print(f"Starting to combine {length} PDFs: {file_paths}")

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

        for file_path in file_paths:
            file_name = file_path.split('/')[-1]

            # trim off the .pdf extension
            if file_name.endswith('.pdf') or file_name.endswith('.PDF'):
                file_name = file_name[:-4]

            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                merger.append_pages_from_reader(pdf_reader)
                new_outline = merger.add_outline_item(file_name, page_num)
                insert_bookmarks(pdf_reader, pdf_reader.outline, new_outline)
                page_num += len(pdf_reader.pages)

        merger.write("merged-pdf.pdf")
        merger.close()

        print("Finished combining PDFs!")


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
