#.\.venv\Scripts\Activate.ps1
import time
import cv2
import glob
import os
from threading import Thread
from emailing import send_email
from datetime import datetime

# Thêm cv2.CAP_DSHOW để Windows mở camera nhanh và không bị treo
video = cv2.VideoCapture(0)
time.sleep(1)
first_frame = None
status_list = []
count = 1
current_images = []
current_day = datetime.now().day

while True:
    status = 0

    check, frame = video.read()
    if not check:
        print("Không đọc được tín hiệu từ camera!")
        break
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    #cv2.imshow("Video", dil_frame)

    # Find and draw contours on the original BGR frame
    contours, _ = cv2.findContours(
        dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        status = 1
    
    if status == 1:
        image_path = f"images/{count}.png"
        cv2.imwrite(image_path, frame)
        current_images.append(image_path)
        count = count + 1

    status_list.append(status)
    status_list=status_list[-2:]
    print(status_list)

    if status_list[0] == 1 and status_list[1] == 0:
        if current_images:
            image_with_object = current_images[len(current_images) // 2]
            email_thread = Thread(target=send_email, args=(image_with_object, current_images))
            email_thread.daemon = True
            email_thread.start()
        current_images = []

    # --- KIỂM TRA RESET VÀO 12H ĐÊM KHI KHÔNG CÓ KHÁCH ---
    today = datetime.now().day
    if today != current_day and status == 0: #status = 0 means no customer
        count = 1
        current_day = today
        print(f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}] Đã sang ngày mới, reset bộ đếm count = 1!")
        
        # Show the bounding box view in a separate window
    cv2.imshow("Video", frame)

    key = cv2.waitKey(100)
    if key == ord("q"): 
        break
video.release()
