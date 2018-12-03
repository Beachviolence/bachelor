// INFORMARSJON //

// Filnavn: wirelesstransmitter.ino

// Forfatter: Simon Strandvold og Hans Petter Leines

// Beskrivelse:
// Denne koden er lastet opp på arduinobrettet som
// mottar kommando via USB fra datamaskin og sender
// videre til dronen trådløst

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN 10

const byte slaveAddress[5] = {'R','x','A','A','A'};
RF24 radio(CE_PIN, CSN_PIN);

int dataToSend = -1;

unsigned long currentMillis;
unsigned long prevMillis;
unsigned long txIntervalMillis = 1000;

void setup() {

    Serial.begin(9600);

    Serial.println("Tx Starting");

    radio.begin();
    radio.setDataRate( RF24_250KBPS );
    radio.setRetries(3,5);
    radio.openWritingPipe(slaveAddress);
}

//====================

void loop() {
    while (!Serial.available());
    dataToSend = Serial.read();
    currentMillis = millis();
    if (currentMillis - prevMillis >= txIntervalMillis) {
        send();
        prevMillis = millis();
    }
}

//====================

void send() {

    bool rslt;
    rslt = radio.write( &dataToSend, sizeof(dataToSend) );

    Serial.print("Data Sent ");
    Serial.print(dataToSend);
    if (rslt) {
        Serial.println("  Acknowledge received");
    }
    else {
        Serial.println("  Tx failed");
    }
}
