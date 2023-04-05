import sys
import os
import configparser
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QSizePolicy, QDialog, QScrollArea, QCheckBox, QMessageBox, QFrame
from PyQt6.QtGui import QGuiApplication, QClipboard
from message_parser import MessageParser
from typing import OrderedDict, Tuple

basedir = os.path.dirname(__file__)

try:
	# Only applicable for Windows application
    from ctypes import windll
    myappid = 'rkcoding.fixv.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def get_fix_dict_path(app_config: dict) -> Tuple[dict, dict]:
	if 'TransportDataDictionary' in app_config and 'AppDataDictionary' in app_config:
		transport_dict_path = os.path.join(basedir, app_config['TransportDataDictionary'])
		appl_dict_path = os.path.join(basedir, app_config['AppDataDictionary'])
		return (transport_dict_path, appl_dict_path)
	if 'DataDictionary' in app_config:
		data_dict_path = os.path.join(basedir, app_config['DataDictionary'])
		return (data_dict_path, None)
	return (None, None)

def get_clipboard(clipboard: QClipboard) -> str:
	mime_data = clipboard.mimeData()
	if mime_data.hasText():
		return mime_data.text()
	return ''

def set_clipboard(clipboard: QClipboard, source: str):
	clipboard.setText(source)


class ScrollLabel(QScrollArea):
	def __init__(self, parent = None) -> None:
		super().__init__(parent)
		self.setWidgetResizable(True)
		content = QWidget(self)
		self.setWidget(content)
		content_vbox = QVBoxLayout(content)
		label = QLabel(content)
		content_vbox.addWidget(label)
		self.label = label

	def setText(self, text):
		self.label.setText(text)

	def text(self):
		return self.label.text()

	def clear(self):
		self.label.clear()

class AppConfig():
	expand_on_launch = True

class MessageEditor(QDialog):
	apply_signal = QtCore.pyqtSignal()

	def __init__(self, parent = None) -> None:
		super().__init__(parent)
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Message Editor')
		self.setModal(True)
		# self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

		central_vbox = QVBoxLayout()
		toolbar_hbox = QHBoxLayout()
		toolbar_hbox.setSpacing(5)
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
		button_box.addStretch()
		button_box.addWidget(cancel_button)

		self.msg_text_edit = msg_text_edit
		self.clipboard = QGuiApplication.clipboard()

		copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, msg_text_edit.toPlainText()))
		paste_button.clicked.connect(lambda: msg_text_edit.setText(get_clipboard(self.clipboard)))
		clear_button.clicked.connect(msg_text_edit.clear)
		cancel_button.clicked.connect(lambda: self.close())
		apply_button.clicked.connect(self.apply_signal)

class AppWindow(QMainWindow):
	def __init__(self, app: QtWidgets.QApplication) -> None:
		super().__init__()

		# Setting up app config and initialize message parser
		app_config_file_name = 'app_config.ini'
		app_config = configparser.ConfigParser()
		if len(app_config.read(os.path.join(basedir, app_config_file_name))) == 0:
			QMessageBox.warning(self, "Error",
		       f"""<p>Config file not found. Please ensure that "{app_config_file_name}" file exists.</p>
			   <p>Application will now exit.</p>""",
			   QMessageBox.StandardButton.Ok)
			sys.exit()
		if not app_config.defaults:
			QMessageBox.warning(self, "Error",
		       f"""<p>Error reading in config file. Please ensure that config file is in correct format.</p>
			   <p>Application will now exit.</p>""",
			   QMessageBox.StandardButton.Ok)
			sys.exit()
		default_config = app_config['DEFAULT']

		self.msg_parser = None
		if default_config:
			data_dict_path, appl_dict_path = get_fix_dict_path(default_config)
			if data_dict_path or appl_dict_path:
				self.msg_parser = MessageParser(data_dict_path, appl_dict_path)

		if not self.msg_parser:
			QMessageBox.warning(self, "Error",
		       f"""<p>Quickfix dictionary path incorrectly set. Please check the config file.</p>
			   <p>Application will now exit.</p>""",
			   QMessageBox.StandardButton.Ok)
			sys.exit()
		self.app = app
		self.init_ui()
		self.init_logic()
		self.show()

	def init_ui(self):
		self.setObjectName('MainWindow')
		self.setWindowTitle('Fix Message Viewer')
		self.resize(500, 600)
		self.move(0, 0)
		self.setup_actions()
		self.setup_menu()

		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)

		central_vbox = QVBoxLayout()

		compact_container = QWidget()
		compact_container.setStyleSheet('background-color:#bbbbbb;')
		# compact_container.setStyleSheet('background-color:#85e0ff;')
		# compact_container.setContentsMargins(4, 4, 4, 4)
		# compact_vbox = QVBoxLayout()
		# compact_vbox.setContentsMargins(0, 0, 0, 0)
		# compact_frame = QFrame()
		# compact_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# compact_frame.setStyleSheet('background-color:black;')
		# compact_line.setLineWidth(3)
		# compact_label = QLabel('Expand')
		# compact_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		# compact_label.setContentsMargins(5, 5, 5, 5)
		# compact_label.setStyleSheet('QLabel { color : white; background-color : black; }')

		viewer_container = QWidget()
		viewer_vbox = QVBoxLayout()
		viewer_vbox.setContentsMargins(0, 0, 0, 0)
		viewer_vbox.setSpacing(10)

		toolbar_hbox = QHBoxLayout()
		toolbar_hbox.setContentsMargins(0, 0, 0, 0)
		toolbar_hbox.setSpacing(20)
		compact_button = QPushButton('Compact')

		msg_entry_vbox = QVBoxLayout()
		msg_entry_vbox.setSpacing(0)
		title_hbox = QHBoxLayout()
		title_hbox.setSpacing(5)
		title_hbox.setContentsMargins(0, 0, 0, 10)
		msg_title_label = QLabel('Fix Message')
		msg_title_label.setContentsMargins(5, 0, 5, 0)
		msg_title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
		autopaste_checkbox = QCheckBox('AutoPaste  ')
		seperator_line = QFrame()
		seperator_line.setFrameShape(QFrame.Shape.VLine)
		copy_button = QPushButton('Copy')
		paste_button = QPushButton('Paste')
		clear_button = QPushButton('Clear')
		msg_line = QTextEdit()
		msg_line.setReadOnly(True)
		text_height = msg_line.document().documentLayout().documentSize().height()
		msg_line.setFixedHeight(int(text_height) + 15)
		msg_line.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

		actions_hbox = QHBoxLayout()
		parse_button = QPushButton('Re-Parse')

		output_tree = QTreeWidget()
		output_tree.setColumnCount(3)
		output_tree.setHeaderLabels(['Tag', 'Name', 'Value'])


		CENTRAL_VBOX = True
		# COMPACT_VBOX = True
		VIEWER_VBOX = True
		TOOLBAR_HBOX = True
		MSG_ENTRY_VBOX = True
		TITLE_HBOX = True
		ACTIONS_HBOX = True

		central_widget.setLayout(central_vbox)
		if CENTRAL_VBOX:
			central_vbox.addWidget(compact_container)
			# compact_container.setLayout(compact_vbox)

			# if COMPACT_VBOX:
				# compact_vbox.addWidget(compact_label)
				# compact_vbox.addWidget(compact_frame)

			central_vbox.addWidget(viewer_container)
			viewer_container.setLayout(viewer_vbox)

			if VIEWER_VBOX:
				viewer_vbox.addLayout(toolbar_hbox)
				viewer_vbox.addLayout(msg_entry_vbox)
				viewer_vbox.addLayout(actions_hbox)

				if TOOLBAR_HBOX:
					toolbar_hbox.addWidget(compact_button)

				if MSG_ENTRY_VBOX:
					msg_entry_vbox.addLayout(title_hbox)

					if TITLE_HBOX:
						title_hbox.addWidget(msg_title_label)
						title_hbox.addStretch()
						title_hbox.addWidget(autopaste_checkbox)
						title_hbox.addWidget(seperator_line)
						title_hbox.addWidget(copy_button)
						title_hbox.addWidget(paste_button)
						title_hbox.addWidget(clear_button)

					msg_entry_vbox.addWidget(msg_line)

				if ACTIONS_HBOX:
					actions_hbox.addWidget(parse_button)
					actions_hbox.addStretch()

				viewer_vbox.addWidget(output_tree)


		## Export variable to self
		self.central_vbox = central_vbox
		self.central_widget = central_widget
		self.compact_container = compact_container
		# self.compact_label = compact_label
		self.viewer_container = viewer_container
		self.compact_button = compact_button
		self.autopaste_checkbox = autopaste_checkbox
		self.msg_title_label = msg_title_label
		self.copy_button = copy_button
		self.paste_button = paste_button
		self.clear_button = clear_button
		self.parse_button = parse_button
		self.msg_line = msg_line
		self.output_tree = output_tree
		self.message_editor = MessageEditor()
		self.clipboard = QGuiApplication.clipboard()

	def setup_actions(self):
		self.auto_compact_act = QtGui.QAction('&Auto Compact')
		self.auto_compact_act.setCheckable(True)
		self.auto_compact_act.setShortcut('Ctrl+O')
		self.auto_compact_act.toggled.connect(self.toggle_autocompact)
		self.edit_message_act = QtGui.QAction('&Edit Message')
		self.edit_message_act.setShortcut('Ctrl+E')
		self.edit_message_act.triggered.connect(self.show_message_editor)
		self.always_top_act = QtGui.QAction('&Always On Top')
		self.always_top_act.setShortcut('Ctrl+T')
		self.always_top_act.setCheckable(True)
		self.always_top_act.toggled.connect(self.toggle_stays_on_top)
		self.always_top_act.toggle()

	def setup_menu(self):
		edit_menu = self.menuBar().addMenu("Edit")
		edit_menu.addAction(self.edit_message_act)
		view_menu = self.menuBar().addMenu("View")
		view_menu.addAction(self.auto_compact_act)
		view_menu.addAction(self.always_top_act)

	def init_logic(self):
		self.is_compact = False
		self.is_autocompact = False

		self.message_editor.apply_signal.connect(self.apply_message_editor)
		self.compact_container.mousePressEvent = lambda _: self.toggle_compact(False)
		# self.compact_label.mousePressEvent = lambda _: self.toggle_compact(False)
		self.compact_button.clicked.connect(lambda: self.toggle_compact(True))
		self.autopaste_checkbox.toggled.connect(self.toggle_autopaste)
		self.copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, self.msg_line.toPlainText()))
		self.paste_button.clicked.connect(self.paste_and_decode)
		self.clear_button.clicked.connect(self.msg_line.clear)
		self.parse_button.clicked.connect(self.decode_and_show_msg)
		self.msg_line.mousePressEvent = self.show_message_editor
		self.compact_container.setVisible(False)
		self.prev_size = self.size()
		self.toggle_compact_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+M'), self)
		self.toggle_compact_sc.activated.connect(lambda: self.toggle_compact(not self.is_compact))
		self.toggle_autopaste_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Shift+P'), self)
		self.toggle_autopaste_sc.activated.connect(lambda: self.autopaste_checkbox.toggle())
		self.paste_decode_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+P'), self)
		self.paste_decode_sc.activated.connect(self.paste_and_decode)
		# self.toggle_autopaste.activated.connect(lambda: print('toggle'))

	def toggle_compact(self, is_compact: bool):
		if self.message_editor.isVisible():
			return
		# prev_inner_frame_x = self.geometry().topLeft().x()
		# prev_pos = self.pos()
		# frame_height = self.frameSize().height() - self.size().height()
		self.viewer_container.setVisible(not is_compact)
		self.compact_container.setVisible(is_compact)
		if is_compact:
			self.menuBar().hide()
			self.central_vbox.setContentsMargins(0, 0, 0, 0)
			self.prev_size = self.size()
			self.mousePressEvent
		else:
			self.menuBar().show()
			self.central_vbox.setContentsMargins(10, 10, 10, 10)
		# self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_compact)
		# self.compact_label.adjustSize()
		# self.compact_container.adjustSize()
		# self.central_widget.adjustSize()
		self.adjustSize()
		# self.resize(self.prev_size if not is_compact else QtCore.QSize(self.size().width(), self.compact_label.minimumHeight()))
		# self.resize(self.prev_size if not is_compact else QtCore.QSize(self.size().width(), self.compact_line.minimumHeight()))
		self.resize(self.prev_size if not is_compact else QtCore.QSize(self.size().width(), 12))
		# print(self.sizeHint())
		# self.resize(self.prev_size if not is_compact else QtCore.QSize(0, 0))
		# if is_compact:
		# 	self.move(prev_inner_frame_x, prev_pos.y() - frame_height)
		# else:
		# 	self.resize(self.prev_size)
		# 	self.move(prev_inner_frame_x, prev_pos.y())
		# self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, is_compact)
		# self.show()
		self.is_compact = is_compact

	def toggle_stays_on_top(self, checked):
		self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, checked)
		self.show()

	def autopaste_decode(self):
		if self.message_editor.isVisible():
			return
		self.paste_and_decode()

	def toggle_autopaste(self, checked: bool):
		if checked:
			self.clipboard.changed.connect(self.autopaste_decode)
		else:
			self.clipboard.changed.disconnect(self.autopaste_decode)

	def changeEvent(self, e: QtCore.QEvent) -> None:
		if e.type() == QtCore.QEvent.Type.ActivationChange:
			if self.isActiveWindow():
				if self.is_compact:
					self.toggle_compact(False)
			else:
				if self.is_autocompact and not self.is_compact:
					self.toggle_compact(True)
		return super().changeEvent(e)

	# def on_focus_changed(self):
	# 	if not self.isActiveWindow() and not self.is_compact:
	# 		self.toggle_compact(True)

	def toggle_autocompact(self, checked: bool):
		self.is_autocompact = checked
		# if checked:
		# 	self.app.focusChanged.connect(self.on_focus_changed)
		# else:
		# 	self.app.focusChanged.disconnect(self.on_focus_changed)

	def show_message_editor(self, *arg):
		if self.is_compact:
			return
		self.message_editor.msg_text_edit.setText(self.msg_line.toPlainText())
		self.message_editor.show()

	def apply_message_editor(self):
		self.msg_line.setText(self.message_editor.msg_text_edit.toPlainText())
		self.message_editor.close()
		self.decode_and_show_msg()

	def paste_and_decode(self):
		self.msg_line.setText(get_clipboard(self.clipboard).replace('\n', '').replace('\r', ''))
		self.decode_and_show_msg()

	def decode_and_show_msg(self):
		try:
			msg_dict = self.msg_parser.parse_msg(self.msg_line.toPlainText())
			self.setup_output_tree(msg_dict)
		except Exception as error:
			QMessageBox.warning(self, "Error",
		       f"""<h2>Message Parsing Error</h2>
			   <p>{type(error).__name__}: {error}</p>""",
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

	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName('FIX Viewer')
	app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "assets", "appicon.ico")))
	app_window = AppWindow(app)

	# msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|10=225|'
	# app_window.msg_line.setText(msg_string)
	# app_window.msg_label.setMinimumSize(app_window.msg_label.minimumSizeHint())

	sys.exit(app.exec())
