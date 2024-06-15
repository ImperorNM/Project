import json
from tkinter import *

low_hsv = (0, 0, 0)
high_hsv = (255, 255, 255)


def save_data():
    global low_hsv, high_hsv
    print(listbox.curselection())
    if listbox.curselection() == (0,):
        curselection = True
    else:
        curselection = False
    data = {
        "lowHue": low_hsv[0],
        "lowSaturation": low_hsv[1],
        "lowValue": low_hsv[2],
        "highHue": high_hsv[0],
        "highSaturation": high_hsv[1],
        "highValue": high_hsv[2],
        "openScreen": curselection
    }
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(data, file)

def set_color(color):
    global low_hsv, high_hsv
    if color == "pink":
        low_hsv = (113, 90, 40)
        high_hsv = (171, 195, 165)
    elif color == "orange":
        low_hsw = (0, 145, 90)
        high_hsv = (184, 212, 232)
    elif color == "green":
        low_hsv = (45, 100, 20)
        high_hsv = (100, 200, 220)

if __name__ == "__main__":
    root = Tk()
    root.title("abc")
    root.geometry("500x400")

    label1 = Label(text="Color >>>", font="Arial 26")
    label1.place(x=10, y=30)
    pinkButton = Button(text="pink", font="Arial 10", command=lambda: set_color("pink"), width=10, height=5)
    pinkButton.place(x=200, y=10)
    orangeButton = Button(text="yellow", font="Arial 10", command=lambda: set_color("orange"), width=10, height=5)
    orangeButton.place(x=300, y=10)
    greenButton = Button(text="green", font="Arial 10", command=lambda: set_color("green"), width=10, height=5)
    greenButton.place(x=400, y=10)

    label1 = Label(text="OpenCameraWindows >>>", font="Arial 20")
    label1.place(x=10, y=155)
    listbox = Listbox(listvariable=Variable(value=["Да", "Нет"]), width=10, height=5)
    listbox.place(x=350, y=140)

    saveButton = Button(text="Save", font="Arial 24", command=lambda: save_data(), width=10, height=2)
    saveButton.place(x=150, y=250)

    root.mainloop()
