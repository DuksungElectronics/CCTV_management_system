import cv2
import datetime
import glob
import os
import re
import threading


def get_file_name_from_datetime(start_dt, end_dt):
    start, end = str(start_dt), str(end_dt)
    start, end = start.replace(":", ";"), end.replace(":", ";")
    start, end = "["+start.replace(" ", "]"), "["+end.replace(" ", "]")

    return start+"_"+end

def get_datetime_str_from_edited_file_name(fn):
    fn = fn.replace(";", ":").replace("[", "").replace("]", " ")
    return fn

def get_theft_time_list(parent_path="./theft_videos", extension="*.mp4"):
    video_paths = glob.glob(os.path.join(parent_path, extension))
    for i, path in enumerate(video_paths):
        video_paths[i] = os.path.basename(path)
        video_paths[i] = get_datetime_str_from_edited_file_name(video_paths[i]).replace(extension[1:],"")

    return video_paths

def get_edited_file_name_from_datetime(dt):
    dt = str(dt)
    dt = dt.replace(":", ";")
    dt = "["+dt.replace(" ", "]")

    return dt

def get_datetime_from_string(string, format="default", video_extension="*.mp4"):
    if format == "default":
        date_time_obj = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        return date_time_obj
    elif format == "video_file":
        string = string.replace(video_extension[1:], "")
        from_to = string.split("_")
        start = datetime.datetime.strptime(from_to[0], '[%Y-%m-%d]%H;%M;%S')
        end = datetime.datetime.strptime(from_to[1], '[%Y-%m-%d]%H;%M;%S')
        return start, end
    else:
        return



def get_video_paths_to_read(start, end, parent_path = "./video", extension="*.mp4"):
    video_paths = glob.glob(os.path.join(parent_path, extension))
    # video_paths.sort()
    start_idx, end_idx = -1, -1
    for idx, video in enumerate(video_paths):

        start_time, end_time = get_datetime_from_string(os.path.basename(video), format="video_file")

        # video_paths에 비디오 파일 이름이 오름차순 정렬되어 있을 시 기준
        if start >= start_time and start < end_time:
            start_idx = idx
        if end <= end_time and end > start_time:
            end_idx = idx
            break

    if start_idx == -1:
        print("start point file missing")
        print("No Video Files from", start, "to", end)
        return
    if end_idx == -1:
        print("end point file missing")
        return

    for video_file in video_paths[:start_idx]:
        try:
            os.remove(video_file)
        except OSError as e:
            print("Error: %s : %s" % (video_file, e.strerror))

    return video_paths[start_idx:end_idx+1]



def save_theft_time_cctv_video(theft_time, timiedelta, save_signal, video_saved, videos_parent_path="./video", save_path="./theft_videos"):
    theft_time = get_datetime_from_string(theft_time)

    start_time, end_time = theft_time - timiedelta, theft_time + timiedelta
    print("=====================================================================")
    print(f"[{threading.current_thread().name}]", "Theft occurred at", theft_time, "!")
    print(f"[{threading.current_thread().name}]", f"Get video clip from {start_time} to {end_time} ...")

    videos = get_video_paths_to_read(start_time, end_time, parent_path=videos_parent_path)

    if videos is None:
        print(f"[{threading.current_thread().name}]", "No recorded file! needed file is recording !")
        print(f"[{threading.current_thread().name}]", "wait for saving the video...")
        save_signal.set()
        video_saved.wait()


    videos = get_video_paths_to_read(start_time, end_time, parent_path=videos_parent_path)
    print(f"[{threading.current_thread().name}]", videos)
    if videos is None:
        return -1
    # print(f"[{threading.current_thread().name}]", videos)

    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 인코딩 포맷 문자
    fps = 30
    size = (640, 480)  # 프레임 크기

    # Create a new video
    file_name_to_save = get_edited_file_name_from_datetime(theft_time) + ".mp4"
    file_name_to_save = os.path.join(save_path, file_name_to_save)
    new_video = cv2.VideoWriter(file_name_to_save, fourcc, fps, size)

    for idx, video in enumerate(videos):
        file_start_time, file_end_time = get_datetime_from_string(os.path.basename(video), format="video_file")
        cap = cv2.VideoCapture(video)

        if not cap.isOpened():
            print(f"[{threading.current_thread().name}]", "fail to open the video file !")
            return -1

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        # calculate crop start point of the video file
        start_time_to_crop = (start_time - file_start_time).total_seconds()
        start_frame = int(start_time_to_crop * fps)

        if start_frame < 0:
            start_time_to_crop = 0
            start_frame = 0

        if start_frame >= frame_count:
            continue

        # calculate crop end point of the video file
        end_time_to_crop = (end_time - file_start_time).total_seconds()
        end_frame = int(end_time_to_crop * fps)

        if end_frame < 0 or end_frame > frame_count:
            end_time_to_crop = duration
            end_frame = frame_count

        print(f"[{threading.current_thread().name}]", f"video {idx}: ---------------------------")
        print(f"[{threading.current_thread().name}]", os.path.basename(video))
        print(f"[{threading.current_thread().name}]", 'fps = ' + str(fps))
        print(f"[{threading.current_thread().name}]", 'number of frames = ' + str(frame_count))
        print(f"[{threading.current_thread().name}]", 'duration (S) = ' + str(duration))
        print(f"[{threading.current_thread().name}]", f"{start_time_to_crop}:{end_time_to_crop}", start_frame, end_frame)

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        read_cnt = 0
        while read_cnt < (end_frame - start_frame):

            r, frame = cap.read()
            if not r:
                break
            # Write the frame
            new_video.write(frame)

            read_cnt += 1

        cap.release()

    new_video.release()
    return 0


def record_CCTV(auto_saving_interval, q=None):
    terminate_proc = False

    cap = cv2.VideoCapture(0)

    if cap.isOpened:
        fps = 25
        fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 인코딩 포맷 문자
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        size = (int(width), int(height))  # 프레임 크기
        print(size)

        while not terminate_proc:
            rec_start_time = datetime.datetime.now().replace(microsecond=0)
            file_path = './video/' + re.sub(':| ', '-', str(rec_start_time)) + '.mp4'
            print(file_path)

            out = cv2.VideoWriter(file_path, fourcc, fps, size)  # VideoWriter 객체 생성

            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.imshow('camera-recording', frame)
                    out.write(frame)  # 파일 저장
                    sig = 0
                    if q is not None:
                        if q.qsize() > 0:
                            sig = q.get()
                    if (datetime.datetime.now() - rec_start_time).total_seconds() > auto_saving_interval or sig == -1:
                        break
                    if cv2.waitKey(int(1000 / fps)) != -1:
                        terminate_proc = True
                else:
                    print('no file!')
                    break
            out.release()  # 파일 닫기
    else:
        print("Can`t open camera!")

    cap.release()
    cv2.destroyAllWindows()


