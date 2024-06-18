import cv2
import numpy as np
import threading

class DetectorObj:
    def __init__(self):
        pass

    def detect_objects(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 19, 5)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        objects_contours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 2000:
                objects_contours.append(cnt)

        return objects_contours

parameters = cv2.aruco.DetectorParameters_create()
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_50)

pixel_cm_ratio = None
lock = threading.Lock()

def process_frame(frame):
    global pixel_cm_ratio
    img = frame.copy()

    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:
        int_corners = np.int0(corners)
        cv2.polylines(img, int_corners, True, (0, 255, 0), 5)

        aruco_perimeter = cv2.arcLength(corners[0], True)

        with lock:
            pixel_cm_ratio = aruco_perimeter / 20

        detector = DetectorObj()
        contours = detector.detect_objects(img)

        for cnt in contours:
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            box = cv2.boxPoints(rect)
            box = np.int0(box)

            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            cv2.polylines(img, [box], True, (255, 0, 0), 2)
            cv2.putText(img, "Width {} cm".format(round(object_width, 1)), (int(x - 100), int(y - 20)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            cv2.putText(img, "Height {} cm".format(round(object_height, 1)), (int(x - 100), int(y + 15)),
                        cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

    cv2.imshow("Image", img)

def read_camera(cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        process_frame(frame)
        if cv2.waitKey(1) == 27:
            break

def main():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    threading.Thread(target=read_camera, args=(cap,), daemon=True).start()
    cv2.destroyAllWindows()
    cap.release()

if __name__ == "__main__":
    main()
