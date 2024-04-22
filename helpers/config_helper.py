import xml.etree.ElementTree as ET

def load_config(xml_template_file = "default.xml") -> list:
    # Read the XML template from the file
    with open(xml_template_file, 'r') as file:
        xml_template = file.read()

    fields = []
    for child in ET.fromstring(xml_template):
        field_name = child.get("name")
        field_type = child.get("type")
        fields.append((field_name, field_type))

    return fields

def get_config_dict(xml_template_file = "default.xml") -> dict:
    tree = ET.parse(xml_template_file)
    root = tree.getroot()
    index_dict = {}
    
    # Parse <value> elements
    for value in root.findall('value'):
        name = value.get('name')
        index = list(root).index(value)
        index_dict[name] = index
    
    # Parse <const> elements
    for const in root.findall('const'):
        name = const.get('name')
        index = list(root).index(const)
        index_dict[name] = index

    # for default config:
    # {'NodeType': 1, 'FullAddress': 2, 'ShortAddress': 3, 'SoftwareVersion': 4, 'ChannelMask': 5, 'PanID': 6, 'WorkingChannel': 7, 'ParentAddress': 8, 'LQI': 9, 'RSSI': 10, 'Command_ID': 0}
    return index_dict

def get_value_dict(xml_template_file = "default.xml") -> dict:
    tree = ET.parse(xml_template_file)
    root = tree.getroot()
    value_dict = {}
    
    # Parse <value> elements
    for value in root.findall('value'):
        name = value.get('name')
        value_dict[name] = value.text
    
    return value_dict

print(get_value_dict())