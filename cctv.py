

import datetime

from threading import Thread, Event
from queue import Queue

from threadWork import record_CCTV, save_video, edit_theft_video

VIDEO_SAVING_INTERVAL = 60 * 10       # sec

TIME_DELTA_TO_LOOK = datetime.timedelta(seconds=5)   # 도난 의심 시간대 기준으로 앞뒤로 얼마만큼의 영상을 볼 것인지
VIDEO_PATH = "./video"

videoSaveQ = Queue()

video_save_signal = Event()
video_saved_event = Event()


cam_th = Thread(name="Webcam", target=record_CCTV, args = (VIDEO_SAVING_INTERVAL, videoSaveQ, video_save_signal, ), daemon=True)
writer_th = Thread(name="Webcam Writer", target=save_video, args = (videoSaveQ, video_saved_event, ), daemon=True)
editor_th = Thread(name="Editor", target=edit_theft_video, args = (TIME_DELTA_TO_LOOK, video_save_signal, video_saved_event, VIDEO_PATH, ), daemon=True)

cam_th.start()
writer_th.start()
editor_th.start()

cam_th.join()
writer_th.join()
editor_th.join()