__author__ = 'matthewpang'
from Tkinter import *
import pickle
import time

root = Tk()
root.title("Fucking Machine Test Interface")

# Define Frame
control_frame = Frame(root)
button_frame = Frame(control_frame)
mode_frame = Frame(control_frame)
switch_frame = Frame(control_frame)

slider_frame = Frame(root)

reset = IntVar()


def resetter(dump):
    reset.set(1)


def slapper_defaults():
    inner_slider.set(3)
    outer_slider.set(3)
    max_speed.set(100)
    min_speed.set(20)


def gobetween_defaults():
    inner_slider.set(0.5)
    outer_slider.set(0.5)
    max_speed.set(8)
    min_speed.set(8)


def speedroutine_defaults():
    inner_slider.set(0.5)
    outer_slider.set(0.5)
    max_speed.set(100)
    min_speed.set(20)
    step_adjust.set(5)


def threesome_defaults():
    inner_slider.set(1)
    outer_slider.set(1)
    max_speed.set(20)
    min_speed.set(20)
    max_slider.set(240)
    min_slider.set(180)
    # min_slider.configure(to=180)
    # min_speed.configure(background="red")
    # step_adjust.configure(background="red")


spacer = Canvas(root, width=30, height=1)
spacer.pack(side=LEFT)

on_off = IntVar()
Canvas(switch_frame, width=1, height=1).pack()
Checkbutton(switch_frame, text="ON/OFF", variable=on_off, font="TimesNewRoman 44 bold").pack()

switch_frame.pack()

spacer = Canvas(control_frame, width=1, height=10)
spacer.pack()

mode_label = Label(mode_frame, text="Mode", font="TimesNewRoman 30 bold").pack()
Canvas(mode_frame, width=1, height=1).pack()
mode = IntVar()
Radiobutton(mode_frame, text="GoBeetween", variable=mode, value=0, command=gobetween_defaults,
            font="TimesNewRoman 28").pack()
Canvas(mode_frame, width=1, height=1).pack()

Radiobutton(mode_frame, text="SpeedCrossing", variable=mode, value=1, command=speedroutine_defaults,
            font="TimesNewRoman 28").pack()
Canvas(mode_frame, width=1, height=1).pack()
Radiobutton(mode_frame, text="FastSlow", variable=mode, value=2, command=speedroutine_defaults,
            font="TimesNewRoman 28").pack()
Canvas(mode_frame, width=1, height=1).pack()
Radiobutton(mode_frame, text="Slapper", variable=mode, value=3, command=slapper_defaults,
            font="TimesNewRoman 28").pack()
Canvas(mode_frame, width=1, height=1).pack()
Radiobutton(mode_frame, text="Threesome", variable=mode, value=4, command=threesome_defaults,
            font="TimesNewRoman 28").pack()
Canvas(mode_frame, width=1, height=1).pack()

mode_frame.pack()

Canvas(control_frame, width=1, height=10).pack()

golabel = Label(button_frame, text="Go To", font="TimesNewRoman 30 bold").pack()
button_frame.pack()
Canvas(button_frame, width=1, height=1).pack()

# go_zero_label = Label(root,text = "Go to Zero").pack()
go_zero = IntVar()
go_zero.set(0)


def go_zero_setter():
    go_zero.set(1)


Button(button_frame, text=" Zero", command=go_zero_setter, font="TimesNewRoman 28").pack()
Canvas(button_frame, width=1, height=1).pack()

# go_min_label = Label(root,text = "Go to Minimum").pack()
go_min = IntVar()
go_min.set(0)


def go_min_setter():
    go_min.set(1)


Button(button_frame, text="Minimum", command=go_min_setter, font="TimesNewRoman 28").pack()
Canvas(button_frame, width=1, height=1).pack()

go_max = IntVar()
go_max.set(0)


def go_max_setter():
    go_max.set(1)


Button(button_frame, text="Maximum", command=go_max_setter, font="TimesNewRoman 28").pack()

Canvas(button_frame, width=1, height=30).pack()

control_frame.pack(side=LEFT)

max_slider = Scale(slider_frame, from_=135, to=240, orient=HORIZONTAL, resolution=5, tickinterval=15, length=600,
                   label="Maximum Depth", width=45, font="TimesNewRoman 12 bold")
max_slider.set(240)
max_slider.pack()

stroke_slider = Scale(slider_frame, from_=15, to=135, orient=HORIZONTAL, resolution=1, tickinterval=10, length=600,
                   label="Stroke Length", width=45, font="TimesNewRoman 12 bold")
stroke_slider.set(15)
stroke_slider.pack()

inner_slider = Scale(slider_frame, from_=0.5, to=10, orient=HORIZONTAL, resolution=0.5, length=600,
                     label="Delay at Minimum Position", width=45, font="TimesNewRoman 12 bold")
inner_slider.set(0.5)
inner_slider.pack()

outer_slider = Scale(slider_frame, from_=0.5, to=10, orient=HORIZONTAL, resolution=0.5, length=600,
                     label="Delay at Maximum Position", width=45, font="TimesNewRoman 12 bold")
outer_slider.set(0.5)
outer_slider.pack()

max_speed = Scale(slider_frame, from_=8, to=100, orient=HORIZONTAL, resolution=1, length=600, command=resetter,
                  label="Max Speed", width=45, font="TimesNewRoman 12 bold")
max_speed.set(8)
max_speed.pack()

min_speed = Scale(slider_frame, from_=8, to=100, orient=HORIZONTAL, resolution=1, length=600, command=resetter,
                  label="Min Speed", width=45, font="TimesNewRoman 12 bold")
min_speed.set(8)
min_speed.pack()

step_adjust = Scale(slider_frame, from_=1, to=20, orient=HORIZONTAL, resolution=1, length=600, command=resetter,
                    label="Speed Step Size (Ramp Speed)", width=45, font="TimesNewRoman 12 bold")
step_adjust.set(5)
step_adjust.pack()

spacer = Canvas(root, width=30, height=1)
spacer.pack(side=LEFT)

slider_frame.pack(side=LEFT)

spacer = Canvas(root, width=30, height=700)
spacer.pack(side=LEFT)

v_zero = IntVar()
v_zero.set(0)


def v_zero_setter():
    v_zero.set(1)


# Button(root,text = "Home and Reset Valves", command=v_zero_setter).pack()

def write():
    file = open('/tmp/stream', 'w')
    a = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    a[0] = on_off.get()
    a[1] = v_zero.get()
    a[2] = stroke_slider.get()
    a[3] = max_slider.get()
    a[4] = inner_slider.get()
    a[5] = outer_slider.get()
    a[6] = max_speed.get()
    a[7] = go_max.get()
    a[8] = go_min.get()
    a[9] = go_zero.get()
    a[10] = step_adjust.get()
    a[11] = min_speed.get()
    a[12] = mode.get()
    a[13] = reset.get()
    pickle.dump(a, file)
    root.after(100, write)


def button_reset():
    if v_zero.get() == 1:
        v_zero.set(0)
    if go_max.get() == 1:
        go_max.set(0)
    if go_min.get() == 1:
        go_min.set(0)
    if go_zero.get() == 1:
        go_zero.set(0)
    if reset.get() == 1:
        reset.set(0)

    root.after(250, button_reset)


root.after(100, write)
root.after(500, button_reset)
root.mainloop()
