import sys
import json
from enum import Enum
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QWidget, QLabel, QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QTreeWidget, QTreeWidgetItem, QSizePolicy
from message_parser import MessageParser
from typing import OrderedDict

class AppConfig():
	expand_on_launch = True

class UiTree(Enum):
	CENTRAL_WIDGET = True
	MAIN_VSTACK = True
	TITLE_HSTACK = True

class AppWindow(QtWidgets.QMainWindow):
	def __init__(self) -> None:
		super().__init__()
		self.setup_ui()
		self.setup_inapp_logic()
		self.show()

	def setup_ui(self):
		build_tree = {

		}
		self.setObjectName("MainWindow")
		self.resize(500, 800)
		self.setWindowTitle("Fix Message Decoder")
		central_widget = QWidget(self)
		central_widget.setObjectName("centralwidget")
		self.setCentralWidget(central_widget)

		if UiTree.CENTRAL_WIDGET:
			main_vlayout = QVBoxLayout()
			central_widget.setLayout(main_vlayout)

			if UiTree.MAIN_VSTACK:

				if UiTree.TITLE_HSTACK:
					title_hlayout = QHBoxLayout()
					main_vlayout.addLayout(title_hlayout)
					input_msg_label = QLabel()
					input_msg_label.setText("Fix Message")
					title_hlayout.addWidget(input_msg_label)

					title_hlayout.addStretch()

					clear_button = QPushButton()
					clear_button.setText("Clear")
					self.clear_button = clear_button
					title_hlayout.addWidget(clear_button)

				msg_edit = QPlainTextEdit()
				msg_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
				msg_edit.setMaximumHeight(msg_edit.fontMetrics().lineSpacing() * 3)
				self.msg_edit = msg_edit
				main_vlayout.addWidget(msg_edit)

				parse_button = QPushButton()
				parse_button.setText("Parse")
				self.parse_button = parse_button
				main_vlayout.addWidget(parse_button)

				output_tree = QTreeWidget()
				self.output_tree = output_tree
				main_vlayout.addWidget(output_tree)


	def setup_inapp_logic(self):
		self.clear_button.clicked.connect(self.msg_edit.clear)

	def setup_output_tree(self, msg_dict: OrderedDict) -> QTreeWidget:
		self.output_tree.setColumnCount(3)
		self.output_tree.setHeaderLabels(['Tag', 'Name', 'Value'])
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
	app_window.msg_edit.setPlainText(msg_string)

	def decode_and_show_msg():
		msg_dict = msg_parser.parse_msg(msg_string)
		app_window.setup_output_tree(msg_dict)

	app_window.parse_button.clicked.connect(decode_and_show_msg)
	# print(json.dumps(msg_dict, indent=2))

	sys.exit(app.exec())