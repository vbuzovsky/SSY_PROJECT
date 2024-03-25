import serial
import string
import argparse
import xml.etree.ElementTree as ET

PORT = "COM3"
BAUDRATE = 38400
PRINTABLE_CHARS = bytes(string.printable, 'ascii')

ser = serial.Serial(
        port=PORT,
        baudrate = BAUDRATE,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0
)

def load_config(xml_template_file ="default.xml") -> list:
    # Read the XML template from the file
    with open(xml_template_file, 'r') as file:
        xml_template = file.read()

    fields = []
    for child in ET.fromstring(xml_template):
        field_name = child.get("name")
        field_type = child.get("type")
        fields.append((field_name, field_type))

    return fields


def sniff() -> None:
    while 1:
            x=ser.read()
            if x:
                if(x in PRINTABLE_CHARS):
                    print(hex(ord(x)))
                else:
                    hex_value = '0x{:02x}'.format(int.from_bytes(x, byteorder='big'))
                    print(hex_value)

def pre_parse(x: bytes) -> bytes:
    if(x in PRINTABLE_CHARS):
        x = hex(ord(x))
    else:
        x = '0x{:02x}'.format(int.from_bytes(x, byteorder='big'))

    return x

def transform_message(buff : list):
    fields = load_config()
    pointer = 0

    print("buffer: ", buff)
    for i, field in enumerate(fields):
        if field[-1][0] == "i":
            sign = True
        else:
            sign = False # use this if neccessary (add to value list)
        
        match field[-1][-1]:
            case '8':
                length = 1
            case '6':
                length = 2
            case '2':
                length = 4
            case '4':
                length = 8
            
        value = buff[pointer:pointer+length]
        print("field: ", field, " value: ", value)
        pointer += length
    # --------------- HEADER ASSEMBLED
        
    additional_start_pointer = 27 # TODO: THIS SHOULD BE CALCULATED BASED ON STRUCT IN LOADED CONFIG
    while 1:
    
        # TODO: ADD SWICH FOR DIFF ADDITIONAL DATA TYPES (1 / 5 / 6 / 7 / 0x20)
        allowed_types = ["0x01", "0x05", "0x06", "0x07", "0x20"]
        if not(buff[additional_start_pointer] in allowed_types):
            print("No additional data.. ending parsing message")
            return

        add_type = buff[additional_start_pointer]
        add_leng = int(buff[additional_start_pointer+1], 0)
        print("add type: ", add_type)
        print("add leng: ", add_leng)

        match add_type:
            case "0x01": # Board type 1 sensors
                data = buff[additional_start_pointer+2:additional_start_pointer+2+add_leng]
                print("data (", add_type, " - sensor data):", data)
            case "0x05": # Packet number
                pass
            case "0x06": # Time stamp
                pass
            case "0x07": # Active period
                pass
            case "0x20": # Node name
                data = buff[additional_start_pointer+2:additional_start_pointer+2+add_leng]
                print("data (", add_type, " - node name):", data)
                ascii_chars = ''.join([chr(int(hex_val, 16)) for hex_val in data])
                print("\n Node name: ", ascii_chars)

        additional_start_pointer += 2 + add_leng # increment pointer to the next add field types
        if(additional_start_pointer >= len(buff)):
            break

    print("\nFINISHED PARSING MESSAGE.\n")
            




def parse():
    prev_byte_start = None
    prev_byte_end = None
    buffer = []

    while 1:
            x=ser.read()
            if x:
                x = pre_parse(x)
                print("current x: ", x)
                
                if prev_byte_start == '0x10' and x == '0x02':
                    
                    # ALL THE FOLLOWING BYTES UNTIL 0x10 x03 ARE DATA TO STORE
                    while 1:
                        if x:
                            if(type(x) != str):
                                x = pre_parse(x)
                            print("(IN DATA LOAD MODE) current x: ", x)
                            buffer.append(x)
                            print("appending to the buffer: ", x)

                            if prev_byte_end == '0x10' and x == '0x03':
                                break
                            prev_byte_end = x
                            x=ser.read()

                    #print("ended loading data")
                    transform_message(buffer[1:-2])
                    buffer.clear()
                    
            
            prev_byte_start = x
                 
        
if __name__ == "__main__":
    print(f"{PORT} opened: ", ser.is_open)
    print("connected to: " + ser.portstr)

    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", type=str, default="true")
    args = parser.parse_args()
    if args.listen.lower() == "true":
        sniff()
    else:
        parse()