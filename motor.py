#### INFORMASJON #### 
# Filnavn: motor.py
# Forfatter: Simon Strandvold og Hans Petter Leines

# Beskrivelse:
# Denne koden henter beste avgjørelse fra det fysiske
# miljøet og skriver det via USB til en arduino
# og videre derfra til dronen

#### BIBLIOTEK ####
import serial
from q_learning import run

# Definerer USB-port som skal leses og skrives på
port = serial.Serial("/dev/ttyACM0",baudrate=9600, timeout=5.0)

# Skriver kontinuerlig anbefalt handling til dronen
epoch = 0
while True:
    input("Trykk enter")
    policy, s = run(epoch)
    action = policy.get(s)
    epoch += 1
    action = action.encode('UTF-8')
    print(action)
    port.write(bytes(action))