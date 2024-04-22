from .parse_hex import hex_to_dec_str

def build_node_information(data) -> dict:
    info = {}

    if len(data) == 1:
        header_data = data[0]

        for h_value in header_data:
            info[h_value[0][0]] = hex_to_dec_str(h_value[1])
        
        return info
    
    else:
        header_data = data[0]
        additional_data = data[1]

        additional_info_dict = {
            '0x01': "Board type 1 sensors",
            '0x05': "Packet number",
            '0x06': "Time stamp",
            '0x07': "Active period",
            '0x20': "Node name"
        }

        for h_value in header_data:
            info[h_value[0][0]] = hex_to_dec_str(h_value[1])

        for a_value in additional_data:
            if a_value[0] in additional_info_dict:
                info[additional_info_dict[a_value[0]]] = hex_to_dec_str(a_value[1])

        return info


    