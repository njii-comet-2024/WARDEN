//map<string, int> controls;

//controls["upArrow"] = 0;
//controls["downArrow"] = 0;

int ENA = 5;
int IN1 = 2;
int IN2 = 3;
int IN3 = 4;
int IN4 = 7;
int ENB = 6;

void setup() {

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  if(serial.available() > 0){
    controls = serial.read();
    serial.write(controls)
    sleep(1000)
  }
}