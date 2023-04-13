import sys
import os
import configparser
import xml.etree.ElementTree as ET
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QSizePolicy, QDialog, QScrollArea, QCheckBox, QMessageBox, QFrame, QStatusBar
from PyQt6.QtGui import QGuiApplication, QClipboard
from message_parser import MessageParser
from typing import Tuple

basedir = os.path.dirname(__file__)

try:
	# Only applicable for Windows application
    from ctypes import windll
    myappid = 'rkcoding.fixv.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def get_clipboard(clipboard: QClipboard) -> str:
	mime_data = clipboard.mimeData()
	if mime_data.hasText():
		return mime_data.text()
	return ''

def set_clipboard(clipboard: QClipboard, source: str):
	clipboard.setText(source)


class MessageEditor(QDialog):
	apply_signal = QtCore.pyqtSignal()

	def __init__(self, parent = None) -> None:
		super().__init__(parent)
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Message Editor')
		self.setModal(True)

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
		self.msg_text_edit.installEventFilter(self)
		self.clipboard = QGuiApplication.clipboard()

		copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, msg_text_edit.toPlainText()))
		paste_button.clicked.connect(lambda: msg_text_edit.setText(get_clipboard(self.clipboard)))
		clear_button.clicked.connect(msg_text_edit.clear)
		cancel_button.clicked.connect(lambda: self.close())
		apply_button.clicked.connect(self.apply_signal)

	def eventFilter(self, widget, event):
		if event.type() == QtCore.QEvent.Type.KeyPress and widget is self.msg_text_edit:
			if event.key() == QtCore.Qt.Key.Key_Return and self.msg_text_edit.hasFocus():
				self.apply_signal.emit()
		return super().eventFilter(widget, event)

class AppWindow(QMainWindow):
	def __init__(self, app: QtWidgets.QApplication) -> None:
		super().__init__()

		# Setting up app config and initialize message parser
		app_config_file_name = 'app_config.ini'
		self.init_config(os.path.join(basedir, app_config_file_name))
		self.msg_parser = self.build_msg_parser()

		self.app = app
		self.message_editor = MessageEditor()
		self.init_ui()
		self.init_logic()
		self.show()

	def init_config(self, config_path: str):
		app_config = configparser.ConfigParser()
		if len(app_config.read(os.path.join(basedir, config_path))) == 0:
			QMessageBox.warning(self, "Error",
				f"""<p>Config file not found. Please ensure that config file exists.</p>
				<p>Application will now exit.</p>""",
				QMessageBox.StandardButton.Ok)
			sys.exit()
		if 'CONFIG' not in app_config.sections():
			QMessageBox.warning(self, "Error",
				f"""<p>Error reading in config file. Please ensure that config file is in correct format:</p>
				<p>[CONFIG]<br>Option1: ...<br>Option2: ...</p>
				<p>Application will now exit.</p>""",
				QMessageBox.StandardButton.Ok)
			sys.exit()
		config = app_config['CONFIG']

		transport_data_dictionary = config['TransportDataDictionary'] if 'TransportDataDictionary' in config else ''
		app_data_dictionary = config['AppDataDictionary'] if 'AppDataDictionary' in config else ''
		if transport_data_dictionary and app_data_dictionary:
			self.data_dict_path = os.path.join(basedir, transport_data_dictionary)
			self.app_dict_path = os.path.join(basedir, app_data_dictionary)
		else:
			data_dictionary = config['DataDictionary'] if 'DataDictionary' in config else ''
			self.data_dict_path = os.path.join(basedir, data_dictionary) if data_dictionary else ''
			self.app_dict_path = None
		always_on_top = config['AlwaysOnTop'] if 'AlwaysOnTop' in config else None
		self.always_on_top = True if always_on_top and always_on_top == 'Yes' else False
		expand_on_launch = config['ExpandOnLaunch'] if 'ExpandOnLaunch' in config else None
		self.expand_on_launch = True if expand_on_launch and expand_on_launch == 'Yes' else False
		error_on_statusbar = config['ErrorOnStatusbar'] if 'ErrorOnStatusbar' in config else None
		self.error_on_statusbar = True if error_on_statusbar and error_on_statusbar == 'Yes' else False

	def build_msg_parser(self):
		try:
			if self.data_dict_path or self.app_dict_path:
				return MessageParser(self.data_dict_path, self.app_dict_path)
		except Exception as e:
			print(e)
			QMessageBox.warning(self, "Error",
				f"""<p>Could not parse quickfix dictionary file at specified path. Please check the dictionary path in config file.</p>
				<p>Application will now exit.</p>""",
				QMessageBox.StandardButton.Ok)
			sys.exit()

		QMessageBox.warning(self, "Error",
			f"""<p>Quickfix dictionary path incorrectly set. Please check the config file.</p>
			<p>Application will now exit.</p>""",
			QMessageBox.StandardButton.Ok)
		sys.exit()

	def init_ui(self):
		self.setObjectName('MainWindow')
		self.setWindowTitle('FIXV')
		self.resize(500, 600)
		self.move(0, 0)
		self.setup_actions()
		self.setup_menu()

		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)

		central_vbox = QVBoxLayout()

		compact_container = QWidget()
		compact_vbox = QVBoxLayout()
		compact_vbox.setContentsMargins(5, 5, 5, 5)
		compact_vbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		expand_arrow = QLabel()
		expand_arrow.setPixmap(QtGui.QPixmap(os.path.join(basedir, "assets", "DownArrow.png")))

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
		msg_line_hbox = QHBoxLayout()
		msg_line = QTextEdit()
		msg_line.setReadOnly(True)
		text_height = msg_line.document().documentLayout().documentSize().height()
		msg_line.setFixedHeight(int(text_height) + 20)
		msg_line.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
		msg_delim_hbox = QHBoxLayout()
		msg_delim_hbox.setContentsMargins(15, 0, 0, 0)
		msg_delim_hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		msg_delim_label = QLabel('Delimiter:')
		msg_delim_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
		msg_delim_edit = QLineEdit('|')
		msg_delim_edit.setTextMargins(5, 5, 5, 5)
		msg_delim_edit.setMaxLength(1)
		msg_delim_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		msg_delim_edit.setFixedWidth(25)

		actions_hbox = QHBoxLayout()
		parse_button = QPushButton('Re-Parse')

		output_tree = QTreeWidget()
		output_tree.setColumnCount(3)
		output_tree.setHeaderLabels(['Tag', 'Name', 'Value'])

		CENTRAL_VBOX = True
		COMPACT_VBOX = True
		VIEWER_VBOX = True
		TOOLBAR_HBOX = True
		MSG_ENTRY_VBOX = True
		TITLE_HBOX = True
		MSG_LINE_HBOX = True
		MSG_DELIM_HBOX = True
		ACTIONS_HBOX = True

		central_widget.setLayout(central_vbox)
		if CENTRAL_VBOX:
			central_vbox.addWidget(compact_container)
			compact_container.setLayout(compact_vbox)

			if COMPACT_VBOX:
				compact_vbox.addWidget(expand_arrow)

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
					msg_entry_vbox.addLayout(msg_line_hbox)

					if TITLE_HBOX:
						title_hbox.addWidget(msg_title_label)
						title_hbox.addStretch()
						title_hbox.addWidget(autopaste_checkbox)
						title_hbox.addWidget(seperator_line)
						title_hbox.addWidget(copy_button)
						title_hbox.addWidget(paste_button)
						title_hbox.addWidget(clear_button)

					if MSG_LINE_HBOX:
						msg_line_hbox.addWidget(msg_line)
						msg_line_hbox.addLayout(msg_delim_hbox)

						if MSG_DELIM_HBOX:
							msg_delim_hbox.addWidget(msg_delim_label)
							msg_delim_hbox.addWidget(msg_delim_edit)

				if ACTIONS_HBOX:
					actions_hbox.addWidget(parse_button)
					actions_hbox.addStretch()

				viewer_vbox.addWidget(output_tree)


		## Export variable to self
		self.central_vbox = central_vbox
		self.central_widget = central_widget
		self.compact_container = compact_container
		self.viewer_container = viewer_container
		self.compact_button = compact_button
		self.autopaste_checkbox = autopaste_checkbox
		self.msg_title_label = msg_title_label
		self.copy_button = copy_button
		self.paste_button = paste_button
		self.clear_button = clear_button
		self.parse_button = parse_button
		self.msg_line = msg_line
		self.msg_delim_edit = msg_delim_edit
		self.output_tree = output_tree
		self.clipboard = QGuiApplication.clipboard()
		self.statusBar = QStatusBar()

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
		if self.always_on_top:
			self.always_top_act.toggle()
		self.show_err_msg_act = QtGui.QAction('&Show Message')
		self.show_err_msg_act.setCheckable(True)
		self.show_err_status_act = QtGui.QAction('&Show in Status Bar')
		self.show_err_status_act.setCheckable(True)
		self.err_act_grp = QtGui.QActionGroup(self)
		self.err_act_grp.addAction(self.show_err_msg_act)
		self.err_act_grp.addAction(self.show_err_status_act)
		self.err_act_grp.triggered.connect(self.change_error_notification)
		if self.error_on_statusbar:
			self.show_err_status_act.setChecked(True)
			self.change_error_notification(self.show_err_status_act)
		else:
			self.show_err_msg_act.setChecked(True)
			self.change_error_notification(self.show_err_msg_act)

	def setup_menu(self):
		edit_menu = self.menuBar().addMenu('Edit')
		edit_menu.addAction(self.edit_message_act)
		view_menu = self.menuBar().addMenu('View')
		view_menu.addAction(self.auto_compact_act)
		view_menu.addAction(self.always_top_act)
		error_menu = view_menu.addMenu('Error')
		error_menu.addAction(self.show_err_msg_act)
		error_menu.addAction(self.show_err_status_act)

	def init_logic(self):
		self.is_compact = False
		self.is_autocompact = False

		self.message_editor.apply_signal.connect(self.apply_message_editor)
		self.compact_container.mousePressEvent = lambda _: self.toggle_compact(False)
		self.compact_button.clicked.connect(lambda: self.toggle_compact(True))
		self.autopaste_checkbox.toggled.connect(self.toggle_autopaste)
		self.copy_button.clicked.connect(lambda: set_clipboard(self.clipboard, self.msg_line.toPlainText()))
		self.paste_button.clicked.connect(self.paste_and_decode)
		self.clear_button.clicked.connect(self.msg_line.clear)
		self.parse_button.clicked.connect(self.decode_and_show_msg)
		self.msg_line.mousePressEvent = self.show_message_editor
		self.compact_container.setVisible(False)
		self.prev_size = self.size()
		self.prev_compact_size = None
		self.toggle_compact_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+M'), self)
		self.toggle_compact_sc.activated.connect(lambda: self.toggle_compact(not self.is_compact))
		self.toggle_autopaste_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Shift+P'), self)
		self.toggle_autopaste_sc.activated.connect(lambda: self.autopaste_checkbox.toggle())
		self.paste_decode_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+P'), self)
		self.paste_decode_sc.activated.connect(self.paste_and_decode)
		self.reparse_sc = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+R'), self)
		self.reparse_sc.activated.connect(self.decode_and_show_msg)

		self.setStatusBar(self.statusBar)

	def toggle_compact(self, is_compact: bool):
		if self.message_editor.isVisible():
			return
		if is_compact:
			self.prev_size = self.size()
			self.viewer_container.setVisible(False)
			self.compact_container.setVisible(True)
			self.menuBar().hide()
			self.statusBar.hide()
			self.central_vbox.setContentsMargins(0, 0, 0, 0)
		else:
			self.prev_compact_size = self.size()
			self.viewer_container.setVisible(True)
			self.compact_container.setVisible(False)
			self.menuBar().show()
			self.statusBar.show()
			self.central_vbox.setContentsMargins(10, 10, 10, 10)
		self.adjustSize()
		self.resize(self.prev_size if not is_compact else (self.prev_compact_size if self.prev_compact_size else QtCore.QSize(self.size().width(), 12)))
		self.is_compact = is_compact

	def toggle_stays_on_top(self, checked):
		self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, checked)
		self.message_editor.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint, checked)
		self.show()

	def change_error_notification(self, qaction: QtGui.QAction):
		self.is_show_err_msg = False
		self.is_show_err_status = False
		if qaction == self.show_err_msg_act:
			self.is_show_err_msg = True
		elif qaction == self.show_err_status_act:
			self.is_show_err_status = True

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

	def toggle_autocompact(self, checked: bool):
		self.is_autocompact = checked

	def show_message_editor(self, *arg):
		if self.is_compact:
			return
		self.message_editor.msg_text_edit.setText(self.msg_line.toPlainText())
		self.message_editor.move(self.pos())
		self.message_editor.show()

	def apply_message_editor(self):
		self.msg_line.setText(self.message_editor.msg_text_edit.toPlainText())
		self.message_editor.close()
		self.decode_and_show_msg()

	def show_status_bar_msg(self, msg: str):
		self.statusBar.clearMessage()
		self.statusBar.showMessage(msg)
		self.statusBar.setToolTip(msg)

	def paste_and_decode(self):
		self.msg_line.setText(get_clipboard(self.clipboard).replace('\n', '').replace('\r', ''))
		self.decode_and_show_msg()

	def decode_and_show_msg(self):
		if not self.msg_line.toPlainText():
			self.show_status_bar_msg('Nothing to parse')
			return
		try:
			self.output_tree.clear()
			msg_tree = self.msg_parser.parse_msg(self.msg_line.toPlainText(), self.msg_delim_edit.text() if self.msg_delim_edit.text() else '|')
			self.build_output_tree(msg_tree)
			self.show_status_bar_msg('Successfully parsed')
		except Exception as error:
			error_msg = f'[{type(error).__name__}Error] {error}'
			if self.is_show_err_msg:
				QMessageBox.warning(self, "Error", f"""<h2>Message Parsing Error</h2>
					<p>{error_msg}</p>""", QMessageBox.StandardButton.Ok)
			elif self.is_show_err_status:
				self.show_status_bar_msg(error_msg)

	def build_output_tree(self, msg_tree: ET.Element):
		for section in msg_tree.iterfind('./'):
			section_item = QTreeWidgetItem([section.tag])
			self.output_tree.addTopLevelItem(section_item)
			section_item.setExpanded(self.expand_on_launch)
			self.build_tree_item(section, section_item)
		# Only resize the first and second column
		for i in range(2):
			self.output_tree.resizeColumnToContents(i)

	def build_tree_item(self, msg_elem: ET.Element, tree_parent: QTreeWidgetItem):
		for elem in msg_elem.iterfind('./'):
			field_tag = elem.get('number') if 'number' in elem.attrib else elem.tag
			if elem.tag == 'field':
				field_name = elem.get('name') if 'name' in elem.attrib else 'UNDEFINED'
			else:
				field_name = elem.get('name') if 'name' in elem.attrib else None
			field_raw = elem.get('raw') if 'raw' in elem.attrib else None
			field_enum = elem.get('enum') if 'enum' in elem.attrib else None
			field_value = None
			if field_raw:
				if field_enum:
					field_value = f'{field_raw} ({field_enum})'
				else:
					field_value = field_raw
			item_entries = [field_tag]
			if field_name:
				item_entries.append(field_name)
			if field_value:
				if len(item_entries) < 2:
					item_entries.append('')
				item_entries.append(field_value)
			if len(item_entries) > 3:
				print(f'[WARNING] Row for {field_tag} contains more than 3 entries')
			tree_item = QTreeWidgetItem(item_entries)
			if len(item_entries) == 3:
				tree_item.setToolTip(2, field_value)
			tree_parent.addChild(tree_item)
			self.build_tree_item(elem, tree_item)
			tree_item.setExpanded(self.expand_on_launch)

if __name__ == "__main__":

	app = QtWidgets.QApplication(sys.argv)
	app.setApplicationName('FIX Viewer')
	app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, "assets", "appicon.ico")))
	app_window = AppWindow(app)

	# msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|528=10|94959=1234|10=225|'
	# app_window.msg_line.setText(msg_string)

	sys.exit(app.exec())
