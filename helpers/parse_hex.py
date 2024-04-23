def hex_to_dec_str(hex_list: list) -> str:
    hex_string = ""
    for hex_value in reversed(hex_list):
        hex_string += hex_value[2:]
    return hex_string

