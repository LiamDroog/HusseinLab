import serial
import time

def get_pos(ser, cmd="?"):
    ser.write(cmd.encode('UTF-8'))
    out = ser.readline().decode('UTF-8')
    out = out.split(',')
    pos = [out[1].lower().translate({ord(i): None for i in 'mpos:'}), out[2]]
    return pos

# Open grbl serial port
s = serial.Serial('COM4', 115200)

# Open g-code file
f = open('gcode.gcode','r')

# Wake up grbl
s.write(b"\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grbl
for line in f:
    l = line.strip()    # Strip all EOL characters for consistency
    print('Sending: ' + l)
    s.write(l.encode('UTF-8') + '\n'.encode('UTF-8')) # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print(' : ' + grbl_out.strip().decode('UTF-8'))

    # get pos
    #p = get_pos(s)
    #print('X: %s; Y: %s' % (p[0], p[1]))

# Wait here until grbl is finished to close serial port and file.
input("  Press <Enter> to exit and disable grbl.")

# Close file and serial port
f.close()
s.close()

