import quickfix as qf
import re
import xml.etree.ElementTree as ET

class MessageParser():
	def __init__(self, data_dict_path: str = None, appl_dict_path: str = None) -> None:
		self.no_group_type = 'NUMINGROUP'
		self.data_dictionary_path = data_dict_path
		self.appl_dictionary_path = appl_dict_path
		self.data_dictionary = qf.DataDictionary(data_dict_path)
		self.appl_dictionary = qf.DataDictionary(appl_dict_path)
		self.field_dictionary = self.appl_dictionary if self.appl_dictionary else self.data_dictionary

	@staticmethod
	def format_message(message: str, delim: str='|') -> str:
		return re.sub('[\x01]', delim, message)

	@staticmethod
	def inv_format_message(message: str, delim: str='|') -> str:
		return re.sub(f'[{delim}]', '\x01', message)

	def parse_msg(self, msg: str, delim: str = '|') -> ET.Element:
		fix_msg = qf.Message(MessageParser.inv_format_message(msg, delim), self.data_dictionary, self.appl_dictionary, False)
		fix_msg.InitializeXML(self.appl_dictionary_path if self.appl_dictionary_path else self.data_dictionary_path)
		# print(fix_msg.toXML())
		return ET.fromstring(fix_msg.toXML())

if __name__ == "__main__":
	msg_parser = MessageParser('dictionaries/FIXT11.xml', 'dictionaries/FIX50SP2.xml')
	msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|528=10|10=225|'
	msg_tree = msg_parser.parse_msg(msg_string)