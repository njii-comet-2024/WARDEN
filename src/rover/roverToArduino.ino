// map<string, int> controls;

//controls["upArrow"] = 0;
//controls["downArrow"] = 0;

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

RF24 radio(7, 8);
const byte address[5] = {'R','x','a','A','z'};

byte recv[2];

int ENA = 5;
int IN1 = 2;
int IN2 = 3;
int IN3 = 4;
int IN4 = 7;
int ENB = 6;

void setup(){
    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    pinMode(ENB, OUTPUT);

    Serial.begin(9600);
    
    bool begin = radio.begin();
    
    radio.openWritingPipe(address);
    radio.setPALevel(RF24_PA_MAX);
    radio.stopListening(); // set as transmitter
}

void loop(){
    if(Serial.available() > 0){
        recv = Serial.read();
        radio.write(&recv, sizeof(recv));
    }
    
    delay(500)
}