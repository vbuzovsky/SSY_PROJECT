def hex_to_dec_str(hex_list : list) -> str:
    decimal_string = ""
    for hex_value in hex_list:
        # Remove "0x" prefix and convert to decimal
        decimal_value = int(hex_value, 16)
        # Append the decimal value to the string
        decimal_string += str(decimal_value)
    return decimal_string


