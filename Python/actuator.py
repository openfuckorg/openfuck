__author__ = 'matthewpang'
import serial
import time
import pickle
import io

serSolenoid = serial.Serial('/dev/ttyACM0', 115200)
serValves = serial.Serial('/dev/ttyACM1', 115200)


def go(pos=100):
    #print(pos)
    serSolenoid.flushInput()
    serSolenoid.flushOutput()
    serSolenoid.write(chr(pos))


def valveset(valvepos=0):
    #print(valvepos)
    serValves.flushInput()
    serValves.flushOutput()
    serValves.write(chr(valvepos))


def fwdValveSet(valvepos=0):
    #print(valvepos)
    serValves.flushInput()
    serValves.flushOutput()
    serValves.write(chr(valvepos))


def backValveSet(valvepos=0):
    #print(valvepos)
    serValves.flushInput()
    serValves.flushOutput()
    serValves.write(chr(int(valvepos + 101)))


def pistonwait():
    while serSolenoid.inWaiting() > 0:
        serSolenoid.flushInput()
        # print("Flushing")
    while serSolenoid.inWaiting() == 0:
        time.sleep(0.01)
        # print("PistonSleep")
    return

def gobetween(mode, min_position=165, max_position=235, indelay=0, outdelay=0):
    if (on_off == 0) or (mode != 0) or (min_position == max_position):
        return

    backValveSet(min_speed)
    fwdValveSet(max_speed)
    if min_position > max_position:
        min_position, max_position = max_position, min_position
    # if (max_position - min_position) < 15:
    #     min_position = max_position - 15

    pistonwait()
    go(max_position)
    time.sleep(outdelay)
    pistonwait()
    go(min_position)
    time.sleep(indelay)
    pistonwait()
    return


def speed_crossing(min_speed=15, max_speed=100, step=5):
    if (on_off == 0) or (mode != 1) or ((max_slider - stroke_slider) == max_slider):
        return

    fwdValveSet(min_speed)
    backValveSet(max_speed)

    out_speeds = []
    in_speeds = []
    out_speeds += list(range(min_speed, max_speed, step))
    out_speeds += list(range(max_speed, min_speed, -step))
    in_speeds += list(range(max_speed, min_speed, -step))
    in_speeds += list(range(min_speed, max_speed, step))

    speeds = zip(out_speeds, in_speeds)

    for out_speed, in_speed in speeds:
        try:
            read()
        except (IOError, EOFError):
            continue
        if (on_off == 0) or (mode != 1) or (reset == 1):
            return
        fwdValveSet(out_speed)
        backValveSet(in_speed)
        pistonwait()
        go(max_slider)
        time.sleep(outer_slider / 10.0)
        pistonwait()
        go(max_slider - stroke_slider)
        time.sleep(inner_slider / 10.0)


def fastslow(min_speed=15, max_speed=100, step=5):
    if (on_off == 0) or (mode != 2) or ((max_slider - stroke_slider) == max_slider):
        return
    fwdValveSet(min_speed)
    backValveSet(min_speed)

    speeds = []
    speeds += list(range(min_speed, max_speed, step))
    speeds += list(range(max_speed, min_speed, -step))
    for speed in speeds:
        try:
            read()
        except (IOError, EOFError):
            continue
        if (on_off == 0) or (mode != 2) or (reset == 1):
            return
        fwdValveSet(speed)
        backValveSet(speed)
        pistonwait()
        go(max_slider)
        time.sleep(outer_slider / 10.0)
        pistonwait()
        go((max_slider - stroke_slider))
        time.sleep(inner_slider / 10.0)


def slapper(min_speed=15, max_speed=100):
    if (on_off == 0) or (mode != 3) or ((max_slider - stroke_slider) == max_slider):
        return
    fwdValveSet(max_speed)
    backValveSet(min_speed)

    pistonwait()
    go((max_slider - stroke_slider))
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(max_slider)
    time.sleep(outer_slider / 10.0)


def threesome(max_speed=100):
    if (on_off == 0) or (mode != 4) or ((max_slider - stroke_slider) == max_slider):
        return
    fwdValveSet(max_speed)
    backValveSet(max_speed)

    end = max_slider
    start = (max_slider - stroke_slider)
    if end - start < 0:
        start, end = end, start
    if end - start < 60:
        start = end - 60

    notch1 = start + ((end - start) / 2)
    notch2 = notch1 + ((end - start) / 4)
    motioninterval = (end - start) / 3

    pistonwait()
    go(start)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(notch1)
    time.sleep(outer_slider / 10.0)
    pistonwait()
    go(notch1 - motioninterval)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(notch1)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(notch2)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(notch2 - motioninterval)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(notch2)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(end)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(end - motioninterval)
    time.sleep(inner_slider / 10.0)
    pistonwait()
    go(end)
    time.sleep(inner_slider / 10.0)
    pistonwait()


alreadyzero = False

on_off = 0
v_zero = 0
stroke_slider = 0
max_slider = 0
inner_slider = 0
outer_slider = 0
max_speed = 0
go_max = 0
go_min = 0
go_zero = 0
step_adjust = 0
min_speed = 0
mode = 0
reset = 0


def read():
    global on_off
    global v_zero
    global stroke_slider
    global max_slider
    global inner_slider
    global outer_slider
    global max_speed
    global go_max
    global go_min
    global go_zero
    global step_adjust
    global min_speed
    global mode
    global reset
    try:
        with io.open('/tmp/stream', 'rb') as file:
            try:
                a = pickle.load(file)
                success = True
            except(IOError,EOFError):
                print("Pickle IO EOF Error")
                return
            except:
                print("SOME OTHER ERROR")
                time.sleep(0.5)
                return

    except(IOError,EOFError):
        print("File IO Error")
        time.sleep(0.5)
        return

    if success:
        v_zero = a[0]
        on_off = a[1]
        stroke_slider = a[2]
        max_slider = a[3]
        inner_slider = a[4]
        outer_slider = a[5]
        max_speed = a[6]
        go_max = a[7]
        go_min = a[8]
        go_zero = a[9]
        step_adjust = a[10]
        min_speed = a[11]
        mode = a[12]
        reset = a[13]
    else:
        print("Did not write corrupted data")


def main():
    while True:
        try:
            read()
        except:
            pass
        if go_max == 1:
            backValveSet(15)
            fwdValveSet(15)
            time.sleep(0.25)
            pistonwait()
            go(max_slider)
            pistonwait()

        elif go_min == 1:
            backValveSet(15)
            fwdValveSet(15)
            time.sleep(0.25)
            pistonwait()
            go(max_slider - stroke_slider)
            pistonwait()

        elif go_zero == 1:
            backValveSet(15)
            fwdValveSet(15)
            time.sleep(0.25)
            pistonwait()
            go(10)
            pistonwait()


        else:
            # print("Send Valve State")
            if (on_off == 0):
                time.sleep(0.15)

            if (on_off == 1):
                # print("fucking")
                gobetween(mode, int(max_slider - stroke_slider), int(max_slider), inner_slider / 10.0, outer_slider / 10.0)
                speed_crossing(min_speed, max_speed, step_adjust)
                fastslow(min_speed, max_speed, step_adjust)
                slapper(min_speed, max_speed)
                threesome(max_speed)


if __name__ == '__main__':
    main()
