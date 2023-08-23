
from flask import Flask, send_file, render_template
from util import get_edited_file_name_from_datetime, get_theft_time_list

app = Flask(__name__)

@app.route('/play/<market_id>/<t_stamp>')
def get(market_id, t_stamp):
    t_stamp = str(t_stamp).replace('_', ' ')
    fname = get_edited_file_name_from_datetime(t_stamp)
    video_source = "/video/"+fname+".mp4"
    return render_template('play_video.html', market=market_id, timestamp=t_stamp, video_src=video_source)

@app.route('/list/<market_id>')
def show_list(market_id):
    timestamps = get_theft_time_list()
    stamps = []
    for t in timestamps:
        stamps.append([f"/play/{str(market_id)}/{t.replace(' ', '_')}", t])
    return render_template('timestamp_list.html', market=market_id, stamp_list = stamps)

@app.route('/video/<string:videoName>')
def video(videoName):
    return send_file("./theft_videos/"+videoName)

@app.route('/test/<string:videoName>')
def video_test(videoName):
    t_stamp = str(videoName).replace('_', ' ')
    fname = get_edited_file_name_from_datetime(t_stamp)+".mp4"

    return send_file("./theft_videos/"+fname)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
