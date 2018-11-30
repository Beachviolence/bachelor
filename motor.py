#### INFORMASJON #### 
# Forfatter: Simon Strandvold og Hans Petter Leines

# Beskrivelse:
# Denne koden henter beste avgjørelse fra det fysiske
# miljøet og skriver det via USB til en arduino
# og videre derfra til dronen

#### BIBLIOTEK ####
import serial
from q_learning import q_learn

# Definerer USB-port som skal leses og skrives på
port = serial.Serial("/dev/ttyACM0",baudrate=9600, timeout=5.0)

# Skriver kontinuerlig anbefalt handling til dronen
while True:
    input("Trykk enter")
    kommando = q_learn()
    kommando = kommando.encode('UTF-8')
    print(kommando)
    port.write(bytes(kommando))
    #output = port.readline()
    #output = output.decode("utf-8")
    print(output)