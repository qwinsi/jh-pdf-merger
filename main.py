import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QAction, \
    QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget, QLabel, QPlainTextEdit, QSpacerItem, QSizePolicy, QCheckBox, \
    QButtonGroup

from merger import combine_pdf_files, BookmarkMode


# popup a warning dialog
def request_confirmation(msg: str) -> bool:
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Additional Confirmation")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg_box.button(QMessageBox.Ok).setText("Continue")
    msg_box.setDefaultButton(QMessageBox.Cancel)
    result = msg_box.exec()
    return result == QMessageBox.Ok


class MyPlainTextEdit(QPlainTextEdit):
    signal_text_submitted = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            text = self.toPlainText()
            self.signal_text_submitted.emit(self.toPlainText())
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setWindowTitle("File Selection Example")
        self.setGeometry(100, 100, 600, 400)

        # Create a QListWidget to display selected filenames
        self.fileListWidget = QListWidget(self)
        self.fileListWidget.setGeometry(0, 0, 600, 800)
        self.fileListWidget.clicked.connect(self.openFileDialog)

        self.bookmark_enabled_checkbox = QCheckBox("Make bookmark")
        self.bookmark_enabled_checkbox.setChecked(True)
        # a group of radio buttons to select bookmark mode
        self.bookmark_mode_group = QButtonGroup()
        self.bookmark_mode_group.setExclusive(True)
        only_file_name_radio = QCheckBox("from only file names")
        only_file_name_radio.setChecked(True)
        self.bookmark_mode_group.addButton(only_file_name_radio, BookmarkMode.FILE_NAME_AS_BOOKMARK.value)
        both_file_name_and_section_radio = QCheckBox("from file names and bookmarks")
        self.bookmark_mode_group.addButton(both_file_name_and_section_radio,
                                           BookmarkMode.FILE_NAME_AND_SECTION_AS_BOOKMARK.value)

        self.output_path_edit = MyPlainTextEdit(None)
        self.output_path_edit.signal_text_submitted.connect(self.combinePdfs)

        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.fileListWidget)

        verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)

        layout.addWidget(self.bookmark_enabled_checkbox)
        layout.addWidget(self.bookmark_mode_group.buttons()[0])
        layout.addWidget(self.bookmark_mode_group.buttons()[1])

        output_area_layout = QHBoxLayout()
        output_path_label = QLabel("Output Path:")
        output_area_layout.addWidget(output_path_label)
        # height of output_path_edit just fits single line
        self.output_path_edit.setFixedHeight(36)
        output_area_layout.addWidget(self.output_path_edit)
        layout.addLayout(output_area_layout)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.combine_action = QAction("Merge Files", self)
        self.combine_action.triggered.connect(self.combinePdfs)
        self.combine_action.setShortcut("Ctrl+R")
        self.combine_action.setEnabled(False)

        self.clear_action = QAction("Clear Selection", self)
        self.clear_action.triggered.connect(self.clearSelection)


        self._setUpMenuBar()

    def _setUpMenuBar(self):
        # Set up menu bar
        menu = self.menuBar()

        file_menu = menu.addMenu("File")
        open_action = QAction("Add Files", self)
        open_action.triggered.connect(self.openFileDialog)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        file_menu.addAction(self.clear_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        # bind ctrl+q on Windows/Linux or cmd+q on Mac to exit
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        run_menu = menu.addMenu("Run")

        run_menu.addAction(self.combine_action)

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

        if len(files) > 0:
            # Add selected filenames to the QListWidget
            self.fileListWidget.addItems(files)
            self.combine_action.setEnabled(True)
            output_path = self.output_path_edit.toPlainText()
            if not output_path.endswith(".pdf") and not output_path.endswith(".PDF"):
                # set default output path to be the same as the last selected file
                last_item = files[-1]
                index = last_item.rfind('/')
                base_path = last_item[:index]
                default_output_name = "merge-output.pdf"
                self.output_path_edit.setPlainText(f"{base_path}/{default_output_name}")

    def clearSelection(self):
        self.fileListWidget.clear()
        self.combine_action.setEnabled(False)

    def combinePdfs(self):
        if not self.combine_action.isEnabled():
            return

        output_path = self.output_path_edit.toPlainText()
        # popup a warning dialog if output file name does not end with .pdf
        if not output_path.endswith(".pdf") and not output_path.endswith(".PDF"):
            ok = request_confirmation('Output file name is recommended to end with ".pdf" or ".PDF" '
                                      'but what you entered is not.'
                                      '\nContinue to use this file name as output anyway?')
            if not ok:
                return
        # popup a warning dialog if output file already exists
        if QtCore.QFile.exists(output_path):
            ok = request_confirmation(f"A file named {output_path} already exists. Continue to overwrite?")
            if not ok:
                return

        length = self.fileListWidget.count()
        file_paths = [self.fileListWidget.item(i).text() for i in range(length)]
        print(f"Starting to combine {length} PDFs: {file_paths}")

        combine_pdf_files(file_paths, output_path, BookmarkMode.FILE_NAME_AND_SECTION_AS_BOOKMARK)

        print("Finished combining PDFs!")

        ok_msg_box = QMessageBox()
        ok_msg_box.setWindowTitle("Success")
        ok_msg_box.setText("Finished combining PDFs!")
        ok_msg_box.setStandardButtons(QMessageBox.Ok)
        ok_msg_box.exec()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
