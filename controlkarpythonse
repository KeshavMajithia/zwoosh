import serial
import time

try:
    # Define the serial port and baud rate (replace 'COM5' with your Arduino's COM port)
    ser = serial.Serial('COM5', 9600)

    # Wait for a moment to allow the Arduino to initialize
    time.sleep(2)

    while True:
        # Prompt the user for input
        command = input("Enter a command (1-5 to control pan servo, q to quit): ")

        # Send the command to the Arduino
        ser.write(command.encode())

        if command == 'q':
            break

except serial.SerialException:
    print("An error occurred with the serial connection.")
except KeyboardInterrupt:
    pass
finally:
    if 'ser' in locals():
        ser.close()
