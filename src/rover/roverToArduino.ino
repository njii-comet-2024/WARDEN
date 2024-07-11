/*
Receives control code from raspberry pi and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Vito Tribuzio] [@Snoopy-0]

Date last modified: 07/11/2024
*/
// Libraries
#include <stdio.h>
#include <string.h>
#include <iostream>

int ENA = 5;
int IN1 = 2;
int IN2 = 3;
int IN3 = 4;
int IN4 = 7;
int ENB = 6;

struct inputControls = {
    float leftTread;
    float rightTread;
    float leftWhegFwd;
    float rightWhegFwd;
    float leftWhegBack;
    float rightWhegBack;
    float cameraTypeToggle;,
    float cameraControlToggle;
    float cameraUp;
    float cameraDown;
    float cameraLeft;
    float cameraRight;
};

inputControls controls;

int cameraControl = 0;
int cameraType = 0;

void setup(){
    pinMode(ENA, OUTPUT);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    pinMode(ENB, OUTPUT);

    Serial.begin(9600);
}

/*
Fake state pattern because I hate C++ state pattern
Keeps track of which state camera type is in [regular or IR] and switches
Starts as regular
0 => regular
1 => IR
*/
void cameraControlState(){
    if(cameraType == 0){
        cameraType = 1;
    }
    else{
        cameraType = 0;
    }
}

/*
Fake state pattern because I hate C++ state pattern
Keeps track of which state camera control is in [telescope or tilt] and switches
Starts as telescope
0 => telescope
1 => tilt
*/
void cameraTypeState(){
    if(cameraControl == 0){
        cameraControl = 1;
    }
    else{
        cameraControl = 0;
    }
}

void loop(){
    if(Serial.available() > 0){
        char input[] = Serial.readStringUntil('\n');
        Serial.print("Received: ");
        Serial.println(input);

        parseInputs();
    }
    
    delay(500)
}

/*
Parses serial input from string to struct
*/
void parseInputs(){
    int i = 0;
    char* parsed[25]; // Holds all input values

    // Splits string by `:` and `,`
    char* tokens = strtok(input, ": ,");
    while(tokens != NULL){
        parsed[i] = tokens;
        tokens = strtok(NULL, ": ,");
        i++;
    }

    // Assigns values to struct
    controls.leftTread = std::stof(parsed[1]);
    controls.rightTread = std::stof(parsed[3]);
    controls.leftWhegFwd = std::stof(parsed[5]);
    controls.rightWhegFwd = std::stof(parsed[7]);
    controls.leftWhegBack = std::stof(parsed[9]);
    controls.rightWhegBack = std::stof(parsed[11]);
    controls.cameraTypeToggle = std::stof(parsed[13]);
    controls.cameraControlToggle = std::stof(parsed[15]);
    controls.cameraUp = std::stof(parsed[17]);
    controls.cameraDown = std::stof(parsed[19]);
    controls.cameraLeft = std::stof(parsed[21]);
    controls.cameraRight = std::stof(parsed[23]);
}