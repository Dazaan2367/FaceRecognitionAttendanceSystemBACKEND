import cv2

class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.releast()

    def get_frame(self):
        ret, frame = self.video.read()
        ret, jpeg = cv2.imencode('.jpg',frame)
        gray = cv2.cvtColor(frame , cv2.COLOR_BGR2RGB)
        return jpeg.tobytes()
    
