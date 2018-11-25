import serial
from q_learning import q_learn

port = serial.Serial("/dev/ttyACM0",baudrate=9600, timeout=5.0)

while True:
    input("Trykk enter")
    kommando = q_learn()
    kommando = kommando.encode('UTF-8')
    print(kommando)
    port.write(bytes(kommando))
    #output = port.readline()
    #output = output.decode("utf-8")
    print(output)