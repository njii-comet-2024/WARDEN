const byte address[5] = {'R','x','a','A','z'};

unsigned char recv[30];
unsigned char send[30];

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
    
}

void loop(){
  // int bytes_read = 0;
  //   if(Serial.available() > 0){
  //       while(bytes_read != 10000){
  //         //send[bytes_read] = Serial.readBytes(recv, 2);
  //         bytes_read++;
  //       }
  //     radio.write(&send, sizeof(send));
  //     bytes_read = 0;
  //   }
    
  //   delay(500);
}
