import quickfix as qf
import re
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
from typing import Iterable, DefaultDict

class MessageParser():
	def __init__(self, data_dict_path: str = None, appl_dict_path: str = None) -> None:
		self.no_group_type = 'NUMINGROUP'
		self.data_dictionary = qf.DataDictionary(data_dict_path)
		self.appl_dictionary = qf.DataDictionary(appl_dict_path)
		if self.appl_dictionary:
			self.build_field_type_map(appl_dict_path)
		else:
			self.build_field_type_map(data_dict_path)

	@staticmethod
	def format_message(message: str, delim: str='|') -> str:
		return re.sub('[\x01]', delim, message)

	@staticmethod
	def inv_format_message(message: str, delim: str='|') -> str:
		return re.sub(f'[{delim}]', '\x01', message)

	def build_field_type_map(self, data_dictionary_xml) -> DefaultDict:
		self.field_type_map = defaultdict(lambda: "NOTDEFINED")
		with open(data_dictionary_xml, "r") as f:
			dict_xml = f.read()
			root_tree = ET.fromstring(dict_xml)
			fields = root_tree.find("fields")
			for field in fields.iter("field"):
				self.field_type_map[int(field.attrib["number"])] = field.attrib["type"]

	def msg_to_dict(self, fix_msg: qf.Message):
		root_tree = ET.fromstring(fix_msg.toXML())
		msg_dict = OrderedDict()
		for section in root_tree:
			msg_dict[section.tag] = self.parse_field_value(section)
		return msg_dict

	def parse_field_value(self, field_group: ET.Element):
		tmp_dict = OrderedDict()
		entry_iter = iter(field_group)
		untag_group_index = 0
		while True:
			try:	
				entry = next(entry_iter)
				if (entry.tag == 'field'):
					field_tag = int(entry.get('number'))
					field_value = entry.text
					tmp_dict[field_tag] = self.build_value_dict(field_tag, field_value, entry_iter)
				elif (entry.tag == 'group'):
					print(f'[Warning] Group_{untag_group_index} is not processed')
					tmp_dict[f'Group_{untag_group_index}'] = self.parse_field_value(entry)
					untag_group_index += 1
				else:
					print(f'[WARNING] Unknown xml tag detected: {entry.tag}')
			except StopIteration:
				break
		return tmp_dict

	def build_value_dict(self, tag: int, value: str, entry_iter: Iterable[ET.Element]):
		value_dict = {}
		fix_dict = self.data_dictionary
		if self.appl_dictionary:
			fix_dict = self.appl_dictionary
		if not fix_dict:
			return value_dict
		tag_name = fix_dict.getFieldName(tag, "")[0]
		if not tag_name:
			tag_name = "Undefined tag"
		value_dict["name"] = tag_name
		value_dict["raw"] = value
		translated_value = None
		if fix_dict.hasFieldValue(tag):
			translated_value = fix_dict.getValueName(tag, value, "")[0]
		if not translated_value:
			translated_value = value
		value_dict["value"] = translated_value
		field_type = self.field_type_map[tag]
		value_dict["type"] = field_type
		groups = []
		if field_type == self.no_group_type and value.isdigit():
			for i in range(int(value)):
				next_entry = next(entry_iter)
				if next_entry.tag == 'group':
					groups.append(self.parse_field_value(next_entry))
		value_dict["groups"] = groups
		return value_dict

	def parse_msg(self, msg: str) -> OrderedDict:
		fix_msg = qf.Message(MessageParser.inv_format_message(msg), self.data_dictionary, self.appl_dictionary, False)
		msg_dict = self.msg_to_dict(fix_msg)
		return msg_dict