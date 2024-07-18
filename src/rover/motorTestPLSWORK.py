import serial

# Open serial connection (adjust port and baudrate as per your setup)
ser = serial.Serial('/dev/ttyS0', baudrate=115200, timeout=1)

# Example command to set motor speed
def set_motor_speed(motor_id, speed):
    command = [motor_id, speed]
    checksum = (sum(command) & 0x7F)
    command_packet = bytearray([0x80, motor_id] + command + [checksum])
    ser.write(command_packet)

# Example usage:
set_motor_speed(1, 100)  # Set motor 1 speed to 100