__author__ = 'weigl'

from msmlhook.endpoint import app, start_dispatcher

if __name__ == "__main__":
    start_dispatcher()
    app.run(host="0.0.0.0", debug=True, port=8528)