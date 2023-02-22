import quickfix as qf
import re
import xml.etree.ElementTree as ET
from collections import OrderedDict, defaultdict
import json
from typing import Iterable

def format_message(message: str, delim: str='|'):
	return re.sub('[\x01]', delim, message)

def inv_format_message(message: str, delim: str='|'):
	return re.sub(f'[{delim}]', '\x01', message)

def get_field_type_map(data_dictionary_xml):
	field_type_map = defaultdict(lambda: "NOTDEFINED")
	with open(data_dictionary_xml, "r") as f:
		dict_xml = f.read()
		root_tree = ET.fromstring(dict_xml)
		fields = root_tree.find("fields")
		for field in fields.iter("field"):
			field_type_map[int(field.attrib["number"])] = field.attrib["type"]
	return field_type_map

def msg_to_dict(fix_msg: qf.Message):
	root_tree = ET.fromstring(fix_msg.toXML())
	msg_dict = OrderedDict()
	for section in root_tree:
		msg_dict[section.tag] = parse_field_value(section)
	return msg_dict

def parse_field_value(field_group: ET.Element):
	tmp_dict = OrderedDict()
	entry_iter = iter(field_group)
	untag_group_index = 0
	while True:
		try:	
			entry = next(entry_iter)
			if (entry.tag == 'field'):
				field_tag = int(entry.get('number'))
				field_value = entry.text
				tmp_dict[field_tag] = build_value_dict(field_tag, field_value, entry_iter)
			elif (entry.tag == 'group'):
				print(f'[Warning] Group_{untag_group_index} is not processed')
				tmp_dict[f'Group_{untag_group_index}'] = parse_field_value(entry)
				untag_group_index += 1
			else:
				print(f'[WARNING] Unknown xml tag detected: {entry.tag}')
		except StopIteration:
			break
	return tmp_dict

def build_value_dict(tag: int, value: str, entry_iter: Iterable[ET.Element]):
	value_dict = {}
	if not data_dictionary:
		return value_dict
	tag_name = data_dictionary.getFieldName(tag, "")[0]
	if not tag_name:
		tag_name = "Undefined tag"
	value_dict["name"] = tag_name
	value_dict["raw"] = value
	translated_value = None
	if data_dictionary.hasFieldValue(tag):
		translated_value = data_dictionary.getValueName(tag, value, "")[0]
	if not translated_value:
		translated_value = value
	value_dict["value"] = translated_value
	field_type = field_type_map[tag]
	value_dict["type"] = field_type
	groups = []
	if field_type == no_group_type and value.isdigit():
		for i in range(int(value)):
			next_entry = next(entry_iter)
			if next_entry.tag == 'group':
				groups.append(parse_field_value(next_entry))
	value_dict["groups"] = groups
	return value_dict

fix_dict_path = 'dictionaries/FIX50SP2.xml'
field_type_map = get_field_type_map(fix_dict_path)
data_dictionary = qf.DataDictionary(fix_dict_path)
no_group_type = 'NUMINGROUP'
msg_string = '8=FIX.4.4|9=224|35=D|34=1080|49=TESTBUY1|52=20180920-18:14:19.508|56=TESTSELL1|11=636730640278898634|15=USD|21=2|38=7000|40=1|54=1|55=MSFT|60=20180920-18:14:19.492|453=2|448=111|447=6|802=1|523=test1|448=222|447=8|802=2|523=test2|523=test3|10=225|'

fix_msg = qf.Message(inv_format_message(msg_string), data_dictionary, True)
msg_dict = msg_to_dict(fix_msg)

# print(fix_msg.toXML())
print(json.dumps(msg_dict, indent=2))