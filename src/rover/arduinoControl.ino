/*
Receives control code from raspberry pi and runs on rover

@author [Zoe Rizzo]     [@zizz-0]
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

// Servo 3 -- Camera zoom
#define S3_PIN = 0;
Servo cameraZoom;

// all floats to make converting from strings easier [same process for each value] 
struct inputControls = {
    float leftTread;
    float rightTread;
    float leftWheg;
    float rightWheg;
    float cameraTypeToggle;
    float cameraTelescope;
    float cameraTilt;
    float cameraLeft;
    float cameraRight;
    float cameraZoom;
};

inputControls controls;

int cameraType = 0;

int rightSpeed = 0;
int leftSpeed = 0;

int tiltPos = 90;
int swivelPos = 90;
int zoomPos = 90;
int telePos = 0;

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
    cameraZoom.attach(S3_PIN);

    Serial.begin(9600);

    try:
        arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(5)
        print("Serial connection established")
    except serial.SerialException as e:
        print(f"Error opening serial port {e}")
        exit()
}

/*
Fake state pattern because I hate C++ state pattern
Keeps track of which state camera type is in [regular or IR] and switches
Starts as regular
0 => regular
1 => IR
*/
void cameraTypeState(){
    if(cameraType == 0){
        cameraType = 1;
    }
    else{
        cameraType = 0;
    }
}

void loop(){
    if(Serial.available() > 0){
        char input[] = Serial.readStringUntil('\n');
        Serial.print("Received: ");
        Serial.println(input);
    }

    // Serial.println(input);

    // parseInput();
    // drive();

    // byte cameraPos[] = {byte(tiltPos), byte(swivelPos), byte(telePos), byte(zoomPos)};
    // arduino.write(cameraPos);
}

/*
Parses serial input from string to struct
*/
void parseInput(){
    int i = 0;
    char* parsed[20]; // Holds all input values

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
    controls.leftWheg = std::stof(parsed[5]);
    controls.rightWheg = std::stof(parsed[7]);
    controls.cameraTypeToggle = std::stof(parsed[9]);
    controls.cameraTelescope = std::stof(parsed[11]);
    controls.cameraTilt = std::stof(parsed[13]);
    controls.cameraLeft = std::stof(parsed[15]);
    controls.cameraRight = std::stof(parsed[17]);
    controls.cameraZoom = std::stof(parsed[19]);
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

    // 3-way switches backwards -- 
    // fwd => -1
    // back => 1
    if(controls.leftWheg < 0){
        // stepper motor
        digitalWrite(M6_ENA, HIGH);
        digitalWrite(M6_DIR, HIGH);

        digitalWrite(M6_OPTO, HIGH); 
        digitalWrite(M6_OPTO, LOW);
    }

    if(controls.leftWheg > 0){
        // stepper motor
        digitalWrite(M6_ENA, HIGH);
        digitalWrite(M6_DIR, LOW);

        digitalWrite(M6_OPTO, HIGH); 
        digitalWrite(M6_OPTO, LOW);
    }

    if(controls.rightWheg < 0){
        // stepper motor
        digitalWrite(M5_ENA, HIGH);
        digitalWrite(M5_DIR, HIGH);

        digitalWrite(M5_OPTO, HIGH); 
        digitalWrite(M5_OPTO, LOW);
    }

    if(controls.rightWheg > 0){
        // stepper motor
        digitalWrite(M5_ENA, HIGH);
        digitalWrite(M5_DIR, LOW);

        digitalWrite(M3_OPTO, HIGH); 
        digitalWrite(M3_OPTO, LOW);
    }

    if(controls.cameraTelescope < 0){
        // telescope up
        // stepper motor
        digitalWrite(M7_IN1, HIGH); // may be backwards, need to test
        digitalWrite(M7_IN2, LOW);
        // if telePos < MAX NUM -- FIND OUT MAX
        telePos += 1;
    }

    if(controls.cameraTelescope > 0){
        // telescope down
        // stepper motor
        digitalWrite(M7_IN1, LOW) // may be backwards, need to test
        digitalWrite(M7_IN2, HIGH)

        if(telePos > 0){
            telePos -= 1;
        }
    }

    if(controls.cameraTilt < 0){
        // tilt up
        if(tiltPos < 180){
            tiltPos += 1;
        }
        cameraTilt.write(tiltPos);
    }

    if(controls.cameraTilt > 0){
        // tilt down
        if(tiltPost > 0){
            tiltPos -= 1;
        }
        cameraTilt.write(tiltPos);
    }

    if(controls.cameraLeft > 0){
        // swivel left
        if(swivelPos > 0){
            swivelPos -= 1;
        }
        cameraSwivel.write(swivelPos);
    }

    if(controls.cameraRight > 0){
        // swivel right
        if(swivelPos < 180){
            swivelPos += 1;
        }
        cameraSwivel.write(swivelPos);
    }

    if(controls.cameraTypeToggle > 0){
        cameraTypeState();
    }

    if(controls.cameraZoom > 0){
        if(zoomPos < 180){
            zoomPos += 1;
        }

        cameraZoom.write(zoomPos);
    }

    if(controls.cameraZoom < 0){
        if(zoomPos < 180){
            zoomPos -= 1;
        }

        cameraZoom.write(zoomPos);
    }
}

/*
Converts analog input from -1-1 to 0-255
*/
void convertAnalog(){
    rightSpeed = abs(controls.rightTread * 255);
    leftSpeed = abs(controls.leftTread * 255);
}
