import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QSizePolicy, QDialog, QScrollArea, QCheckBox, QMessageBox
from PyQt6.QtGui import QGuiApplication, QClipboard
from message_parser import MessageParser
from typing import OrderedDict

def get_clipboard(clipboard: QClipboard) -> str:
	mime_data = clipboard.mimeData()
	if mime_data.hasText():
		return mime_data.text()
	return ''

def set_clipboard(clipboard: QClipboard, source: str):
	clipboard.setText(source)


class AppConfig():
	expand_on_launch = True

class MessageEditor(QDialog):
	def __init__(self, msg_label: QLabel, parent = None) -> None:
		super().__init__(parent)
		self.msg_label = msg_label
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Message Editor')
		self.setModal(True)
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

		central_vbox = QVBoxLayout()
		toolbar_hbox = QHBoxLayout()
		copy_button = QPushButton('Copy')
		paste_button = QPushButton('Paste')
		clear_button = QPushButton('Clear')
		msg_text_edit = QTextEdit()
		msg_text_edit.setWordWrapMode(QtGui.QTextOption.WrapMode.WrapAnywhere)

		apply_button = QPushButton('Apply')
		apply_button.setDefault(True)
		cancel_button = QPushButton('Cancel')
		button_box = QHBoxLayout()

		self.setLayout(central_vbox)
		central_vbox.addLayout(toolbar_hbox)
		toolbar_hbox.addWidget(copy_button)
		toolbar_hbox.addWidget(paste_button)
		toolbar_hbox.addWidget(clear_button)
		central_vbox.addWidget(msg_text_edit)
		central_vbox.addLayout(button_box)
		button_box.addWidget(apply_button)
		button_box.addWidget(cancel_button)

		self.msg_text_edit = msg_text_edit
		self.clipboard = QGuiApplication.clipboard()

		copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, msg_text_edit.toPlainText()))
		paste_button.clicked.connect(lambda: msg_text_edit.setText(get_clipboard(self.clipboard)))
		clear_button.clicked.connect(msg_text_edit.clear)
		cancel_button.clicked.connect(lambda: self.close())
		apply_button.clicked.connect(self.apply_changes)
	
	def apply_changes(self):
		self.msg_label.setText(self.msg_text_edit.toPlainText())
		self.close()

	def set_message(self):
		self.msg_text_edit.setText(self.msg_label.text())

class AppWindow(QMainWindow):
	def __init__(self, app: QtWidgets.QApplication, msg_parser: MessageParser) -> None:
		super().__init__()
		self.app = app
		self.msg_parser = msg_parser
		self.init_ui()
		self.init_logic()
		self.show()

	def init_ui(self):
		self.setObjectName('MainWindow')
		self.setWindowTitle('Fix Message Viewer')
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)
		self.resize(400, 600)
		self.setup_actions()
		self.setup_menu()

		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)

		central_vbox = QVBoxLayout()
		central_vbox.setContentsMargins(10, 10, 10, 10)

		compact_container = QWidget()
		compact_vbox = QVBoxLayout()
		compact_vbox.setContentsMargins(0, 0, 0, 0)
		compact_label = QLabel('FIXV')
		compact_label.setStyleSheet('QLabel { color : #abd4ce; }')

		viewer_container = QWidget()
		viewer_vbox = QVBoxLayout()
		viewer_vbox.setContentsMargins(0, 0, 0, 0)
		viewer_vbox.setSpacing(10)

		toolbar_hbox = QHBoxLayout()
		toolbar_hbox.setContentsMargins(0, 0, 0, 0)
		toolbar_hbox.setSpacing(20)
		autopaste_checkbox = QCheckBox('AutoPaste')
		autocompact_checkbox = QCheckBox('AutoCompact')
		compact_button = QPushButton('Compact')

		msg_entry_vbox = QVBoxLayout()
		msg_entry_vbox.setSpacing(0)
		title_hbox = QHBoxLayout()
		title_hbox.setSpacing(5)
		title_hbox.setContentsMargins(0, 0, 0, 0)
		msg_title_label = QLabel('Fix Message')
		msg_title_label.setContentsMargins(5, 5, 5, 0)
		msg_title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
		copy_button = QPushButton('Copy')
		paste_button = QPushButton('Paste')
		clear_button = QPushButton('Clear')
		parse_button = QPushButton('Parse')
		msg_scrollarea = QScrollArea()
		msg_scrollarea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
		msg_label = QLabel()
		msg_scrollarea.setFixedHeight(msg_label.sizeHint().height() + msg_scrollarea.horizontalScrollBar().height())
		msg_label.setContentsMargins(8, 8, 8, 8)
		msg_label.setStyleSheet('QLabel { background-color : #222222; }')

		output_tree = QTreeWidget()
		output_tree.setColumnCount(3)
		output_tree.setHeaderLabels(['Tag', 'Name', 'Value'])


		CENTRAL_VBOX = True
		COMPACT_VBOX = True
		VIEWER_VBOX = True
		TOOLBAR_HBOX = True
		MSG_ENTRY_VBOX = True
		TITLE_HBOX = True

		central_widget.setLayout(central_vbox)
		if CENTRAL_VBOX:
			central_vbox.addWidget(compact_container)
			compact_container.setLayout(compact_vbox)

			if COMPACT_VBOX:
				compact_vbox.addWidget(compact_label)

			central_vbox.addWidget(viewer_container)
			viewer_container.setLayout(viewer_vbox)

			if VIEWER_VBOX:
				viewer_vbox.addLayout(toolbar_hbox)
				viewer_vbox.addLayout(msg_entry_vbox)

				if TOOLBAR_HBOX:
					toolbar_hbox.addWidget(compact_button)
					toolbar_hbox.addStretch()
					toolbar_hbox.addWidget(autopaste_checkbox)
					toolbar_hbox.addWidget(autocompact_checkbox)

				if MSG_ENTRY_VBOX:
					msg_entry_vbox.addLayout(title_hbox)

					if TITLE_HBOX:
						title_hbox.addWidget(msg_title_label)
						title_hbox.addStretch()
						title_hbox.addWidget(copy_button)
						title_hbox.addWidget(paste_button)
						title_hbox.addWidget(clear_button)
						title_hbox.addWidget(parse_button)

					msg_entry_vbox.addWidget(msg_scrollarea)
					msg_scrollarea.setWidget(msg_label)

				viewer_vbox.addWidget(output_tree)


		## Export variable to self
		self.central_widget = central_widget
		self.compact_container = compact_container
		self.compact_label = compact_label
		self.viewer_container = viewer_container
		self.compact_button = compact_button
		self.autopaste_checkbox = autopaste_checkbox
		self.autocompact_checkbox = autocompact_checkbox
		self.msg_title_label = msg_title_label
		self.copy_button = copy_button
		self.paste_button = paste_button
		self.clear_button = clear_button
		self.parse_button = parse_button
		self.msg_label = msg_label
		self.output_tree = output_tree
		self.message_editor = MessageEditor(msg_label)
		self.clipboard = QGuiApplication.clipboard()

	def setup_actions(self):
		self.toggle_mode_act = QtGui.QAction('&Toggle Mode')
		self.toggle_mode_act.setShortcut("Ctrl+T")
		self.toggle_mode_act.triggered.connect(lambda: self.toggle_compact(not self.is_compact))
		self.edit_message_act = QtGui.QAction('&Edit Message')
		self.edit_message_act.setShortcut("Ctrl+E")
		self.edit_message_act.triggered.connect(self.show_message_editor)

	def setup_menu(self):
		edit_menu = self.menuBar().addMenu("Edit")
		edit_menu.addAction(self.edit_message_act)
		view_menu = self.menuBar().addMenu("View")
		view_menu.addAction(self.toggle_mode_act)

	def init_logic(self):
		self.compact_label.mousePressEvent = lambda _: self.toggle_compact(False)
		self.compact_button.clicked.connect(lambda: self.toggle_compact(True))
		self.autopaste_checkbox.toggled.connect(self.toggle_autocopy)
		self.autocompact_checkbox.toggled.connect(self.toggle_autocompact)
		self.copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, self.msg_label.text()))
		self.paste_button.clicked.connect(lambda: self.msg_label.setText(get_clipboard(self.clipboard)))
		self.clear_button.clicked.connect(self.msg_label.clear)
		self.parse_button.clicked.connect(self.decode_and_show_msg)
		self.msg_label.mousePressEvent = self.show_message_editor
		self.compact_container.setVisible(False)
		self.is_compact = False
		self.prev_size = self.size()

	def toggle_compact(self, is_compact: bool):
		if self.message_editor.isVisible():
			return
		self.viewer_container.setVisible(not is_compact)
		self.compact_container.setVisible(is_compact)
		if is_compact:
			self.prev_size = self.size()
		self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_compact)
		self.central_widget.adjustSize()
		self.adjustSize()
		self.resize(self.prev_size if not is_compact else QtCore.QSize(0, 0))
		self.is_compact = is_compact
		self.show()

	def autopaste_decode(self):
		if self.message_editor.isVisible():
			return
		self.paste_clipboard_msg()
		self.decode_and_show_msg()

	def toggle_autocopy(self, checked: bool):
		if checked:
			self.clipboard.changed.connect(self.autopaste_decode)
		else:
			self.clipboard.changed.disconnect(self.autopaste_decode)

	def on_focus_changed(self):
		if not self.isActiveWindow() and not self.is_compact:
			self.toggle_compact(True)

	def toggle_autocompact(self, checked: bool):
		if checked:
			self.app.focusChanged.connect(self.on_focus_changed)
		else:
			self.app.focusChanged.disconnect(self.on_focus_changed)

	def show_message_editor(self, *arg):
		if self.is_compact:
			return
		self.message_editor.set_message()
		self.message_editor.show()
	
	def paste_clipboard_msg(self):
		self.msg_label.setText(get_clipboard(self.clipboard))
	
	def decode_and_show_msg(self):
		try:
			msg_dict = self.msg_parser.parse_msg(self.msg_label.text())
			self.setup_output_tree(msg_dict)
		except Exception as error:
			QMessageBox.warning(self, "Error",
		       f"""<h2>Message Parsing Error</h2>
			   <p>{error}</p>""",
			   QMessageBox.StandardButton.Ok)

	def setup_output_tree(self, msg_dict: OrderedDict) -> QTreeWidget:
		self.output_tree.clear()
		# Fill sections (header, body, trailer)
		for section, section_entries in msg_dict.items():
			tree_item = QTreeWidgetItem([section])
			self.output_tree.addTopLevelItem(tree_item)
			tree_item.setExpanded(AppConfig.expand_on_launch)
			AppWindow.fill_tree_item(tree_item, section_entries)
		for i in range(3):
			self.output_tree.resizeColumnToContents(i)

	def fill_tree_item(item: QTreeWidgetItem, msg_dict: OrderedDict):
		for k, v in msg_dict.items():
			child = QTreeWidgetItem([str(k), str(v['name']), str(v['value'])])
			item.addChild(child)
			child.setExpanded(AppConfig.expand_on_launch)
			groups = v['groups']
			if groups:
				for group in groups:
					AppWindow.fill_tree_item(child, group)


if __name__ == "__main__":

	fix_dict_path = 'dictionaries/FIX50SP2.xml'
	msg_parser = MessageParser(fix_dict_path)

	app = QtWidgets.QApplication(sys.argv)
	app_window = AppWindow(app, msg_parser)

	msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|10=225|'
	app_window.msg_label.setText(msg_string)
	app_window.msg_label.setMinimumSize(app_window.msg_label.minimumSizeHint())

	sys.exit(app.exec())