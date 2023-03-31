import quickfix as qf
import re
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
import json
from typing import Iterable, DefaultDict

class MessageParser():
	def __init__(self, fix_dict_path: str) -> None:
		self.no_group_type = 'NUMINGROUP'
		self.data_dictionary = qf.DataDictionary(fix_dict_path)
		self.build_field_type_map(fix_dict_path)

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
		if not self.data_dictionary:
			return value_dict
		tag_name = self.data_dictionary.getFieldName(tag, "")[0]
		if not tag_name:
			tag_name = "Undefined tag"
		value_dict["name"] = tag_name
		value_dict["raw"] = value
		translated_value = None
		if self.data_dictionary.hasFieldValue(tag):
			translated_value = self.data_dictionary.getValueName(tag, value, "")[0]
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
		fix_msg = qf.Message(MessageParser.inv_format_message(msg), self.data_dictionary, False)
		msg_dict = self.msg_to_dict(fix_msg)
		return msg_dict