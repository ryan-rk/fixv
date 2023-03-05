import sys
import json
from enum import Enum
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QStackedWidget, QSizePolicy, QFrame
from message_parser import MessageParser
from typing import OrderedDict

class AppConfig():
	expand_on_launch = True

class UiTree(Enum):
	CENTRAL_VBOX = True
	COMPACT_VBOX = True
	VIEWER_VBOX = True
	TITLE_HBOX = True

class AppWindow(QtWidgets.QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setup_ui()
		self.init()
		self.show()

	def setup_ui(self):
		self.setObjectName("MainWindow")
		self.setWindowTitle("Fix Message Viewer")
		self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)
		self.resize(400, 600)
		self.setup_actions()
		self.setup_menu()

		central_widget = QWidget(self)
		self.setCentralWidget(central_widget)

		central_vbox = QVBoxLayout()
		central_vbox.setContentsMargins(10,10,10,10)

		compact_container = QWidget()
		compact_vbox = QVBoxLayout()
		compact_vbox.setContentsMargins(0,0,0,0)
		compact_label = QLabel('FIXV')

		viewer_container = QWidget()
		viewer_vbox = QVBoxLayout()
		viewer_vbox.setContentsMargins(10,10,10,10)

		title_hbox = QHBoxLayout()
		msg_title_label = QLabel('Fix Message')
		parse_button = QPushButton('Parse')
		clear_button = QPushButton('Clear')

		msg_label = QLabel('Testing Fix Message to be parsed')
		msg_label.setContentsMargins(5, 5, 5, 5)
		msg_label.setStyleSheet('QLabel { color: black; background-color : #999999; }')
		separator_hline = QFrame()
		separator_hline.setFrameShape(QFrame.Shape.HLine)
		output_tree = QTreeWidget()
		output_tree.setColumnCount(3)
		output_tree.setHeaderLabels(['Tag', 'Name', 'Value'])


		central_widget.setLayout(central_vbox)
		if UiTree.CENTRAL_VBOX:
			central_vbox.addWidget(compact_container)
			compact_container.setLayout(compact_vbox)

			if UiTree.COMPACT_VBOX:
				compact_vbox.addWidget(compact_label)

			central_vbox.addWidget(viewer_container)
			viewer_container.setLayout(viewer_vbox)

			if UiTree.VIEWER_VBOX:
				viewer_vbox.addLayout(title_hbox)

				if UiTree.TITLE_HBOX:
					title_hbox.addWidget(msg_title_label)
					title_hbox.addStretch()
					title_hbox.addWidget(parse_button)
					title_hbox.addWidget(clear_button)

				viewer_vbox.addWidget(msg_label)
				viewer_vbox.addWidget(separator_hline)
				viewer_vbox.addWidget(output_tree)


		## Export variable to self
		self.central_widget = central_widget
		self.compact_container = compact_container
		self.viewer_container = viewer_container
		self.clear_button = clear_button
		self.msg_label = msg_label
		self.output_tree = output_tree

	def setup_actions(self):
		self.toggle_mode_act = QtGui.QAction('&Toggle Mode')
		self.toggle_mode_act.setShortcut("Ctrl+E")
		self.toggle_mode_act.triggered.connect(self.toggle_compact)

	def setup_menu(self):
		view_menu = self.menuBar().addMenu("View")
		view_menu.addAction(self.toggle_mode_act)

	def init(self):
		self.clear_button.clicked.connect(self.msg_label.clear)
		self.compact_container.setVisible(False)
		self.is_compact = False
		self.prev_size = self.size()

	def toggle_compact(self):
		self.viewer_container.setVisible(self.is_compact)
		self.compact_container.setVisible(not self.is_compact)
		if not self.is_compact:
			self.prev_size = self.size()
		self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint, not self.is_compact)
		self.central_widget.adjustSize()
		self.adjustSize()
		self.resize(self.prev_size if self.is_compact else QtCore.QSize(0, 0))
		self.is_compact = not self.is_compact
		self.show()

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
	app_window = AppWindow()

	fix_dict_path = 'dictionaries/FIX50SP2.xml'
	msg_parser = MessageParser(fix_dict_path)
	msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|10=225|'
	# app_window.msg_edit.setPlainText(msg_string)

	def decode_and_show_msg():
		msg_dict = msg_parser.parse_msg(msg_string)
		app_window.setup_output_tree(msg_dict)

	# app_window.parse_button.clicked.connect(decode_and_show_msg)
	# print(json.dumps(msg_dict, indent=2))

	sys.exit(app.exec())