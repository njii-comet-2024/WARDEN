/*
Receives control code from raspberry pi and runs on rover

@author [Zoe Rizzo] [@zizz-0]
        [Vito Tribuzio] [@Snoopy-0]
        [Chris Prol]    [@prolvalone]

Date last modified: 07/11/2024
*/
// Libraries
#include <stdio.h>
#include <string.h>
#include <Servo.h>

// PINS
// IN1 => CLOCKWISE
// IN2 => COUNTER-CLOCKWISE
// Motor 1 -- Right main treads
#define M1_ENA = 0;
#define M1_IN1 = 0;
#define M1_IN2 = 0;

// Motor 2 -- Left main treads
#define M2_ENA = 0;
#define M2_IN1 = 0;
#define M2_IN2 = 0;

// Motor 3 -- Left main treads
#define M3_ENA = 0;
#define M3_IN1 = 0;
#define M3_IN2 = 0;

// Motor 4 -- Left main treads
#define M4_ENA = 0;
#define M4_IN1 = 0;
#define M4_IN2 = 0;

// Motor 5 -- Right wheg treads (DM456AI)
#define M5_ENA = 0;
#define M5_OPTO = 0;
#define M5_DIR = 0;

// Motor 6 -- Left wheg treads  (DM456AI)
#define M6_ENA = 0;
#define M6_OPTO = 0;
#define M6_DIR = 0;

// Motor 7 -- Camera Telescope Linear Actuator
#define M7_IN1 = 0;
#define M7_IN2 = 0;



const int stepsPerRevolution = 200; // for steppers == adjust based on steppers

// Servo 1 -- Camera tilt
#define S1_PIN = 0;
Servo cameraTilt;

// Servo 2 -- Camera swivel
#define S2_PIN = 0;
Servo cameraSwivel;

// all floats to make converting from strings easier [same process for each value] 
struct inputControls = {
    float leftTread;
    float rightTread;
    float leftWhegFwd;
    float rightWhegFwd;
    float leftWhegBack;
    float rightWhegBack;
    float cameraTypeToggle;
    float cameraControlToggle;
    float cameraUp;
    float cameraDown;
    float cameraLeft;
    float cameraRight;
};

inputControls controls;

int cameraControl = 0;
int cameraType = 0;

int rightSpeed = 0;
int leftSpeed = 0;

int tiltPos = 90;
int swivelPos = 90;

void setup(){
    pinMode(M1_ENA, OUTPUT);
    pinMode(M1_IN1, OUTPUT);
    pinMode(M1_IN2, OUTPUT);

    pinMode(M2_ENA, OUTPUT);
    pinMode(M2_IN1, OUTPUT);
    pinMode(M2_IN2, OUTPUT);

    pinMode(M3_ENA, OUTPUT);
    pinMode(M3_IN1, OUTPUT);
    pinMode(M3_IN2, OUTPUT);

    pinMode(M5_ENA, OUTPUT);
    pinMode(M5_OPTO, OUTPUT);
    pinMode(M5_DIR, OUTPUT);

    pinMode(M6_ENA, OUTPUT);
    pinMode(M6_OPTO, OUTPUT);
    pinMode(M6_DIR, OUTPUT);

    pinMode(M7_ENA, OUTPUT);
    pinMode(M7_IN1, OUTPUT);
    PinMode(M7_IN2, OUTPUT);

    cameraTilt.attach(S1_PIN);
    cameraSwivel.attach(S2_PIN);

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
    }

    parseInput();
    drive();
}

/*
Parses serial input from string to struct
*/
void parseInput(){
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

/*
Main drive function -- assigns values to motors and servos
*/
void drive(){
    convertAnalog();

    // Drive motors
    if(controls.rightTread > 0){
        // right tread motors fwd
        digitalWrite(M1_IN1, HIGH);
        digitalWrite(M1_IN2, LOW);
        digitalWrite(M3_IN1, HIGH);
        digitalWrite(M3_IN2, LOW);

        analogWrite(M1_ENA, rightSpeed);
        analogWrite(M3_ENA, rightSpeed);
    }

    if(controls.rightTread < 0){
        // right tread motors back
        digitalWrite(M1_IN1, LOW);
        digitalWrite(M1_IN2, HIGH);
        digitalWrite(M3_IN1, LOW);
        digitalWrite(M3_IN2, HIGH);
        
        analogWrite(M1_ENA, rightSpeed);
        analogWrite(M3_ENA, rightSpeed);
    }

    if(controls.leftTread > 0){
        // left tread motors fwd
        digitalWrite(M2_IN1, HIGH);
        digitalWrite(M2_IN2, LOW);
        digitalWrite(M4_IN1, HIGH);
        digitalWrite(M4_IN2, LOW);
        
        analogWrite(M2_ENA, rightSpeed);
        analogWrite(M4_ENA, rightSpeed);
    }

    if(controls.leftTread < 0){
        // left tread motors back
        digitalWrite(M2_IN1, LOW);
        digitalWrite(M2_IN2, HIGH);
        digitalWrite(M4_IN1, LOW);
        digitalWrite(M4_IN2, HIGH);

        analogWrite(M2_ENA, rightSpeed);
        analogWrite(M4_ENA, rightSpeed);
    }

    if(controls.leftWhegFwd > 0){ // 
        // stepper motor
        digitalWrite(M6_ENA, HIGH);
        digitalWrite(M6_DIR, HIGH);

        digitalWrite(M6_OPTO, HIGH); 
        digitalWrite(M6_OPTO, LOW);
    }

    if(controls.leftWhegBack > 0){
        // stepper motor
        digitalWrite(M6_ENA, HIGH);
        digitalWrite(M6_DIR, LOW);

        digitalWrite(M6_OPTO, HIGH); 
        digitalWrite(M6_OPTO, LOW);
    }

    if(controls.rightWhegFwd > 0){
        // stepper motor
        digitalWrite(M5_ENA, HIGH);
        digitalWrite(M5_DIR, HIGH);

        digitalWrite(M5_OPTO, HIGH); 
        digitalWrite(M5_OPTO, LOW);
    }

    if(controls.rightWhegBack > 0){
        // stepper motor
        digitalWrite(M5_ENA, HIGH);
        digitalWrite(M5_DIR, LOW);

        digitalWrite(M3_OPTO, HIGH); 
        digitalWrite(M3_OPTO, LOW);
    }

    if(controls.cameraUp > 0){
        if(cameraControl == 0){
            // telescope up
            // stepper motor
            digitalWrite(M7_IN1, HIGH); // may be backwards, need to test
            digitalWrite(M7_IN2, LOW);
        }
        else{
            // tilt up 
            tiltPos += 1;
            cameraTilt.write(tiltPos);
        }
    }

    if(controls.cameraDown > 0){
        if(cameraControl == 0){
            // telescope down
            // stepper motor
            digitalWrite(M7_IN1, LOW) // may be backwards, need to test
            digitalWrite(M7_IN2, HIGH)
        }
        else{
            // tilt down
            tiltPos -= 1;
            cameraTilt.write(tiltPos);
        }
    }

    if(controls.cameraLeft > 0){
        // swivel left
        swivelPos -= 1;
        cameraSwivel.write(swivelPos);
    }

    if(controls.cameraRight > 0){
        // swivel right
        swivelPos += 1;
        cameraSwivel.write(swivelPos);
    }

    if(controls.cameraTypeToggle > 0){
        cameraTypeState();
    }

    if(controls.cameraControlToggle > 0){
        cameraControlState();
    }
}

/*
Converts analog input from -1-1 to 0-255
*/
void convertAnalog(){
    rightSpeed = abs(controls.rightTread * 255);
    leftSpeed = abs(controls.leftTread * 255);
}
