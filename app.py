import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QMessageBox, QAction, \
    QVBoxLayout, QHBoxLayout, QFileDialog, QListWidget, QLabel, QPlainTextEdit, QSpacerItem, QSizePolicy, QCheckBox, \
    QButtonGroup, QProgressDialog, QDialog

from merger import merge_pdf_files, BookmarkMode

_APP_NAME = "JH PDF Merger"
_WEBSITE_URL = "https://github.com/qwinsi/jh-pdf-merger"


# popup a warning dialog
def request_confirmation(msg: str, title: str, parent: QWidget) -> bool:
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msg_box.button(QMessageBox.Ok).setText("Continue")
    msg_box.setDefaultButton(QMessageBox.Cancel)
    result = msg_box.exec()
    return result == QMessageBox.Ok


# popup a simple message box
def show_message(msg: str, title: str, parent: QWidget):
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec()


class MyPlainTextEdit(QPlainTextEdit):
    signal_text_submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            text = self.toPlainText()
            self.signal_text_submitted.emit(text)
        else:
            super().keyPressEvent(event)


class UserCancelled(Exception):
    pass


class AboutDialog(QDialog):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setWindowTitle(f"About {_APP_NAME}")
        self.setMinimumSize(360, 120)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"<h1>{_APP_NAME}</h1>"))
        layout.addWidget(QLabel("Version 1.0.0"))
        layout.addWidget(QLabel("This is an open source PDF merger."))
        layout.addWidget(QLabel(f"For more information please visit <a href='{_WEBSITE_URL}'>{_WEBSITE_URL}</a>"))
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._initUI()

    def _initUI(self):
        self.setWindowTitle(_APP_NAME)
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QtGui.QIcon('jh-pdf-merger.ico'))

        # Create a QListWidget to display selected filenames
        self.fileListWidget = QListWidget(self)
        self.fileListWidget.setGeometry(0, 0, 600, 1000)
        self.fileListWidget.clicked.connect(self.openFileDialog)

        self.bookmark_enabled_checkbox = QCheckBox("Make bookmark")
        self.bookmark_enabled_checkbox.setChecked(True)
        # a group of radio buttons to select bookmark mode
        self.bookmark_mode_group = QButtonGroup()
        self._both_file_name_and_section_radio = QCheckBox("from file names and bookmarks")
        self._both_file_name_and_section_radio.setChecked(True)
        self.bookmark_mode_group.addButton(self._both_file_name_and_section_radio,
                                           BookmarkMode.FILE_NAME_AND_SECTION_AS_BOOKMARK.value)
        self.bookmark_mode_group.setExclusive(True)
        self._only_file_name_radio = QCheckBox("from only file names")
        self.bookmark_mode_group.addButton(self._only_file_name_radio, BookmarkMode.FILE_NAME_AS_BOOKMARK.value)

        self.bookmark_enabled_checkbox.stateChanged.connect(
            lambda state: self._toggleBookmarkMode(state == QtCore.Qt.Checked))
        # self.bookmark_enabled_checkbox.stateChanged.connect(lambda state: self.bookmark_mode_group.setEnabled(state))

        self.output_path_edit = MyPlainTextEdit(None)
        self.output_path_edit.signal_text_submitted.connect(self.mergePdfs)

        central_widget = QWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.fileListWidget)

        verticalSpacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(verticalSpacer)

        layout.addWidget(self.bookmark_enabled_checkbox)
        # There should be an indent for the radio buttons. So that the user can know they are related to the checkbox
        hierarchy_layout = QHBoxLayout()
        hierarchy_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        radio_group_layout = QVBoxLayout()
        radio_group_layout.addWidget(self._only_file_name_radio)
        radio_group_layout.addWidget(self._both_file_name_and_section_radio)
        hierarchy_layout.addLayout(radio_group_layout)
        layout.addLayout(hierarchy_layout)

        output_area_layout = QHBoxLayout()
        output_path_label = QLabel("Output Path:")
        output_area_layout.addWidget(output_path_label)
        # height of output_path_edit just fits single line
        self.output_path_edit.setFixedHeight(36)
        output_area_layout.addWidget(self.output_path_edit)
        layout.addLayout(output_area_layout)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.merge_action = QAction("Merge Files", self)
        self.merge_action.triggered.connect(self.mergePdfs)
        self.merge_action.setShortcut("Ctrl+R")
        self.merge_action.setEnabled(False)

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

        run_menu.addAction(self.merge_action)

        help_menu = menu.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.openAboutDialog)
        help_menu.addAction(about_action)

    def _toggleBookmarkMode(self, enabled: bool):
        if enabled:
            self.bookmark_mode_group.setExclusive(True)
            self.bookmark_mode_group.buttons()[0].setChecked(True)
            for button in self.bookmark_mode_group.buttons():
                button.setEnabled(True)
        else:
            self.bookmark_mode_group.setExclusive(False)
            for button in self.bookmark_mode_group.buttons():
                button.setEnabled(False)  # the checkbox gets grey
                button.setChecked(False)

    def getBookmarkMode(self) -> BookmarkMode:
        should_make_bookmark = self.bookmark_enabled_checkbox.isChecked()
        if should_make_bookmark:
            if self._only_file_name_radio.isChecked():
                return BookmarkMode.FILE_NAME_AS_BOOKMARK
            else:
                # assert self._both_file_name_and_section_radio.isChecked()
                return BookmarkMode.FILE_NAME_AND_SECTION_AS_BOOKMARK
        else:
            return BookmarkMode.NO_BOOKMARK

    def openAboutDialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

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
            self.merge_action.setEnabled(True)
            output_path = self.output_path_edit.toPlainText()
            if not output_path.endswith(".pdf") and not output_path.endswith(".PDF"):
                # set default output path to be the same as the last selected file
                last_item = files[-1]
                index = last_item.rfind('/')
                base_path = last_item[:index]
                # use the parent directory if possible
                if base_path.count('/') > 0:
                    index = base_path.rfind('/')
                    base_path = base_path[:index]
                default_output_name = "merge-output.pdf"
                self.output_path_edit.setPlainText(f"{base_path}/{default_output_name}")

    def clearSelection(self):
        self.fileListWidget.clear()
        self.merge_action.setEnabled(False)

    def mergePdfs(self):
        if not self.merge_action.isEnabled():
            return

        output_path = self.output_path_edit.toPlainText()
        # popup a warning dialog if output file name does not end with .pdf
        if not output_path.endswith(".pdf") and not output_path.endswith(".PDF"):
            ok = request_confirmation('Output file name is recommended to end with ".pdf" or ".PDF" '
                                      'but what you entered is not.'
                                      '\nContinue to use this file name as output anyway?',
                                      "Additional Confirmation",
                                      self)
            if not ok:
                return
        # popup a warning dialog if output file already exists
        if QtCore.QFile.exists(output_path):
            ok = request_confirmation(f"A file named {output_path} already exists. Continue to overwrite?",
                                      "Additional Confirmation",
                                      self)
            if not ok:
                return

        length = self.fileListWidget.count()
        file_paths = [self.fileListWidget.item(i).text() for i in range(length)]
        print(f"Starting to merge {length} PDFs: {file_paths}")

        process_dialog = QProgressDialog("Merging PDFs...", "Cancel", 0, len(file_paths), self)
        process_dialog.setMinimumSize(450, 100)
        process_dialog.setWindowTitle("Merging PDFs")
        process_dialog.setWindowModality(QtCore.Qt.WindowModal)

        def tick_callback():
            # For development test use: Sleep 1 seconds to simulate a long-running task
            QtCore.QThread.msleep(100)
            process_dialog.setValue(process_dialog.value() + 1)
            if process_dialog.wasCanceled():
                raise UserCancelled()

        try:
            merge_pdf_files(file_paths, output_path, self.getBookmarkMode(), tick_callback)
        except UserCancelled:
            show_message("You have cancelled the merge operation.", "Cancelled", self)
            print("User cancelled the merge operation.")
            return

        process_dialog.reset()
        print("Finished merging PDFs!")

        show_message("Finished merging PDFs!", "Success", self)


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
