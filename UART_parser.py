import serial
import string
import argparse
from helpers.config_helper import load_config

PORT = "COM3"
BAUDRATE = 38400
PRINTABLE_CHARS = bytes(string.printable, 'ascii')

def sniff(ser) -> None:
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

def transform_message(buff : list) -> list:
    fields = load_config()
    pointer = 0
    # fill this with recieved data, and pass it
    header_data = [] 
    additional_data = []

    print("buffer: ", buff)
    for i, field in enumerate(fields):        
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
        header_data.append([field, value])
        pointer += length
    # --------------- HEADER ASSEMBLED
        
    additional_start_pointer = 27 # TODO: THIS SHOULD BE CALCULATED BASED ON STRUCT IN LOADED CONFIG
    while 1:
        allowed_types = ["0x01", "0x05", "0x06", "0x07", "0x20"]
        if not(buff[additional_start_pointer] in allowed_types):
            print("No additional data.. ending parsing message")
            return

        add_type = buff[additional_start_pointer]
        add_leng = int(buff[additional_start_pointer+1], 0)

        # TODO: IMPLEMENT Additional data types
        match add_type:
            case "0x01": # Board type 1 sensors
                data = buff[additional_start_pointer+2:additional_start_pointer+2+add_leng]
                print("data (", add_type, " - sensor data):", data)
                additional_data.append([add_type, data])
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
                additional_data.append([add_type, data])

        additional_start_pointer += 2 + add_leng # increment pointer to the next addi field types
        if(additional_start_pointer >= len(buff)):
            break
    
    return [header_data, additional_data]
            

def parse(ser_settings, callback=None):
    ser = serial.Serial(**ser_settings)
    prev_byte_start = None
    prev_byte_end = None
    buffer = []

    while 1:
            x=ser.read()
            if x:
                x = pre_parse(x)
                print("current x: ", x)
                if prev_byte_start == '0x10' and x == '0x02':
                
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


                    to_send = transform_message(buffer[1:-2])
                    if callback:
                        callback.emit(to_send)
                    buffer.clear()
                
            prev_byte_start = x


def send_data_to_gui(data, gui_pipe):
    gui_pipe.send(data)

if __name__ == "__main__":
    ser_settings = {
        "port": PORT,
        "baudrate": BAUDRATE,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "bytesize": serial.EIGHTBITS,
        "timeout": 0
    }

    parser = argparse.ArgumentParser()
    parser.add_argument("--listen", type=str, default="true")
    args = parser.parse_args()
    if args.listen.lower() == "true":
        #sniff(ser)
        pass
    else:
        parse(ser_settings)