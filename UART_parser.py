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

    print("buffer: ", buff[1:-2])
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
    additional_start_pointer = 27 # ?
    


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