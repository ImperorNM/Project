from math import *
import json
import cv2
import time
import numpy as np


class Settings:
    xCoordsHistory = []
    yCoordsHistory = []
    coordsHistorySize = 10
    coordsAssumptionIterations = 1

    camera_height = 5
    camera_screen_width = 640
    camera_screen_height = 480
    camera_angle = 100
    calibrationDistance = 100
    calibrationLinearSize = 61  # px

    low_hue = 0
    low_saturation = 0
    low_value = 0
    high_hue = 255
    high_saturation = 255
    high_value = 255
    openScreenWindows = False

    dataFile = "data.json"

    @classmethod
    def get_average_number(cls, massive):
        result = 0
        for element in massive:
            result += abs(element)
        result /= len(massive)
        return result

    @classmethod
    def get_coords(cls, x_px):
        global fwidth, fheight, distanceByCamera
        y = sqrt(distanceByCamera ** 2 - Settings.camera_height ** 2)
        x = 2 * y * (x_px - width / 2) * tan(radians(Settings.camera_angle) / 2) / height
        return round(x), round(y)

    @classmethod
    def save_data(cls, low_hue, low_saturation, low_value, high_hue, high_saturation, high_value, open_screen):
        data = {
            "lowHue": low_hue,
            "lowSaturation": low_saturation,
            "lowValue": low_value,
            "highHue": high_hue,
            "highSaturation": high_saturation,
            "highValue": high_value,
            "openScreen": open_screen
        }

        with open(Settings.dataFile, "w", encoding="utf-8") as file:
            json.dump(data, file)

    @classmethod
    def load_data(cls):
        try:
            with open("data.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            Settings.low_hue = data["lowHue"]
            Settings.low_saturation = data["lowSaturation"]
            Settings.low_value = data["lowValue"]
            Settings.high_hue = data["highHue"]
            Settings.high_saturation = data["highSaturation"]
            Settings.high_value = data["highValue"]
            Settings.openScreenWindows = data["openScreenWindows"]

        except Exception as exeption:
            print(exeption)


def next_coords_assumption():
    if len(Settings.xCoordsHistory) == Settings.coordsHistorySize and len(Settings.yCoordsHistory) == Settings.coordsHistorySize:
        x_assemption_vector = None
        y_assemption_vector = None
        assumption_x = None
        assumption_y = None
        x_vector_coords = list()
        x_coords_history_clone = list(Settings.xCoordsHistory)
        y_vector_coords = list()
        y_coords_history_clone = list(Settings.yCoordsHistory)

        for iteration in range(Settings.coordsAssumptionIterations):
            for i in range(len(x_coords_history_clone) - 1):
                x_vector_coords.append(x_coords_history_clone[i] - x_coords_history_clone[i + 1])
                y_vector_coords.append(y_coords_history_clone[i] - y_coords_history_clone[i + 1])

            if x_coords_history_clone[len(x_coords_history_clone) - 2] < x_coords_history_clone[len(x_coords_history_clone) - 1]:
                x_assemption_vector = Settings.get_average_number(x_vector_coords)
            else:
                x_assemption_vector = -Settings.get_average_number(x_vector_coords)
            if y_coords_history_clone[len(y_coords_history_clone) - 2] < y_coords_history_clone[len(y_coords_history_clone) - 1]:
                y_assemption_vector = Settings.get_average_number(y_vector_coords)
            else:
                y_assemption_vector = -Settings.get_average_number(y_vector_coords)

            assumption_x = x_coords_history_clone[len(x_coords_history_clone) - 1] + x_assemption_vector
            assumption_y = y_coords_history_clone[len(y_coords_history_clone) - 1] + y_assemption_vector
            x_coords_history_clone.append(assumption_x)
            y_coords_history_clone.append(assumption_y)
            x_vector_coords = list()
            y_vector_coords = list()

        return round(assumption_x, 2), round(assumption_y, 2)
        
    elif len(Settings.xCoordsHistory) > Settings.coordsHistorySize and len(Settings.yCoordsHistory) > Settings.coordsHistorySize:
        Settings.xCoordsHistory.pop(0)
        Settings.yCoordsHistory.pop(0)
        next_coords_assumption()

    else:
        return Settings.xCoordsHistory[len(Settings.xCoordsHistory) - 1], Settings.yCoordsHistory[len(Settings.yCoordsHistory) - 1]


if __name__ == "__main__":
    Settings.load_data()

    cam = cv2.VideoCapture(0)
    success, frame = cam.read()
    fheight, fwidth, _ = frame.shape

    while True:
        success, frame = cam.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (Settings.low_hue, Settings.low_saturation, Settings.low_value), (Settings.high_hue, Settings.high_saturation, Settings.high_value))
        cv2.imshow("mask", mask)
        connectivity = 4
        output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_32S)
        num_labels = output[0]
        labels = output[1]
        stats = output[2]

        filtered = np.zeros_like(mask)

        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            topPoint = stats[i, cv2.CC_STAT_TOP]
            leftPoint = stats[i, cv2.CC_STAT_LEFT]
            width = stats[i, cv2.CC_STAT_WIDTH]
            height = stats[i, cv2.CC_STAT_HEIGHT]

            if area >= 500:
                linearSize = sqrt(area)
                distanceByCamera = round(Settings.calibrationDistance * Settings.calibrationLinearSize / linearSize)
                x_ball, y_ball = Settings.get_coords(leftPoint + width / 2)
                Settings.xCoordsHistory.append(x_ball)
                Settings.yCoordsHistory.append(y_ball)
                print(next_coords_assumption())
                assumption_x_ball, assumption_y_ball = next_coords_assumption()
                if -1000 > assumption_x_ball or assumption_x_ball > 1000:
                    assumption_x_ball = "Searching..."
                if -1000 > assumption_y_ball or assumption_y_ball > 1000:
                    assumption_y_ball = "Searching..."

                if Settings.openScreenWindows:
                    filtered[np.where(labels == i)] = 255
                    cv2.putText(frame, f"distance={distanceByCamera}", (leftPoint, topPoint + height + 10), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"linear size={round(linearSize)}", (leftPoint, topPoint + height + 25), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"area={round(area)}", (leftPoint, topPoint + height + 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"x={x_ball}", (leftPoint, topPoint + height + 55), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"y={y_ball}", (leftPoint, topPoint + height + 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"AssumptionX={assumption_x_ball}", (leftPoint, topPoint - 10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv2.LINE_AA)
                    cv2.putText(frame, f"AssumptionY={assumption_y_ball}", (leftPoint, topPoint - 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2, cv2.LINE_AA)

                    cv2.rectangle(frame, (leftPoint, topPoint), (leftPoint + width, topPoint + height), (255, 0, 0), 2)


        cv2.imshow("frame", frame)
        cv2.imshow("mask", mask)
        cv2.imshow("filtered", filtered)

        key = cv2.waitKey(280) & 0xFF
        if key == ord(' '):
            break

    Settings.save_data(Settings.low_hue, Settings.low_saturation, Settings.low_value, Settings.high_hue, Settings.high_saturation, Settings.high_value, True)
    cam.release()
    cv2.destroyAllWindows()
    cv2.waitKey(10)
