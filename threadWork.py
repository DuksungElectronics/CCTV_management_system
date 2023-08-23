import threading
import cv2
import datetime
from util import get_theft_time_list, get_file_name_from_datetime, save_theft_time_cctv_video
import requests
import time

def record_CCTV(auto_saving_interval, videoQ, save_signal):

    print(f"[{threading.current_thread().name}]", "start")
    terminate_proc = False

    cap = cv2.VideoCapture(0)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"[{threading.current_thread().name}]", "FPS:", fps)

    if cap.isOpened:

        while not terminate_proc:
            rec_start_time = datetime.datetime.now().replace(microsecond=0)

            frames = []
            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.putText(frame, str(datetime.datetime.now().replace(microsecond=0)), (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.imshow('camera-recording', frame)
                    frames.append(frame)

                    if (datetime.datetime.now()-rec_start_time).total_seconds() > auto_saving_interval or save_signal.isSet():
                        save_signal.clear()
                        rec_end_time = datetime.datetime.now().replace(microsecond=0)
                        file_name = get_file_name_from_datetime(str(rec_start_time), str(rec_end_time))

                        videoQ.put([file_name, frames.copy()])
                        frames.clear()

                        rec_start_time = datetime.datetime.now().replace(microsecond=0)

                    if cv2.waitKey(1) != -1:
                        terminate_proc = True
                else:
                    print(f"[{threading.current_thread().name}]", 'no file!')
                    break
    else:
        print(f"[{threading.current_thread().name}]", "Can`t open camera!")

    cap.release()
    cv2.destroyAllWindows()

def save_video(videoQ, video_saved):
    print(f"[{threading.current_thread().name}]", "start")
    fps = 30
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 인코딩 포맷 문자
    width = 640
    height = 480
    size = (int(width), int(height))  # 프레임 크기
    print(f"[{threading.current_thread().name}]", size)
    while True:
        video = videoQ.get()

        file_path = "./video/" + video[0] + ".mp4"
        frames = video[1]

        out = cv2.VideoWriter(file_path, fourcc, fps, size)  # VideoWriter 객체 생성
        for f in frames:
            out.write(f)
        out.release()

        print(f"[{threading.current_thread().name}]", "saved video file:", file_path)
        video_saved.set()
        video_saved.clear()

def edit_theft_video(timiedelta, save_signal, video_saved, videos_parent_path="./video"):
    print(f"[{threading.current_thread().name}]", "start")
    parent_url = "http://localhost:8080/theft_time"

    while True:

        new_timestamps = []
        files = get_theft_time_list()
        try:
            response = requests.get(parent_url)
            if (response.status_code != 200):
                print("failed to receive data")
            else:
                datas = response.json()
                for d in datas:
                    if d == "null" or not d:
                        continue
                    if d not in files:
                        new_timestamps.append(d)
                # print(datas)
        except:
            print("Cannot connect to Server!")
        print("New Theft Timestamps:", new_timestamps)
        for theft_time in new_timestamps:
            succ = save_theft_time_cctv_video(str(theft_time), timiedelta, save_signal, video_saved, videos_parent_path)
            if succ == -1:
                print(f"[{threading.current_thread().name}]", "failed to edit video")
            else:
                print(f"[{threading.current_thread().name}]", "succeed to edit video")
