import cv2
import datetime
import os
from util import save_theft_time_cctv_video

TIME_DELTA_TO_LOOK = datetime.timedelta(seconds=3)   # 도난 의심 시간대 기준으로 앞뒤로 얼마만큼의 영상을 볼 것인지
VIDEO_PATH = "./video"

theft_time = "2023-05-03 17:53:04.0000"  # 도난 의심 시간대 (일단 예시)

save_theft_time_cctv_video(theft_time, TIME_DELTA_TO_LOOK, VIDEO_PATH)
