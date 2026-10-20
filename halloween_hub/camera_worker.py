"""Hidden Pi motion scan. Only numerical scores leave this process."""
import json
import os
import signal
import sys
import time


def main():
    parent=os.getppid()
    deadline=time.monotonic()+max(1,min(600,float(sys.argv[1]) if len(sys.argv)>1 else 180))
    from picamera2 import Picamera2
    import numpy as np
    running = True
    def stop(*_):
        nonlocal running
        running = False
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    camera = Picamera2()
    try:
        camera.configure(camera.create_video_configuration(
            main={'size':(320,240),'format':'YUV420'},
            controls={'FrameRate':5},buffer_count=3))
        camera.start()
        print(json.dumps({'ready':True}),flush=True)
        previous = None
        count = 0
        while running and time.monotonic()<deadline and os.getppid()==parent:
            frame = np.rot90(camera.capture_array('main')[:240,:320],k=-1).copy()
            if not running:break
            height,width = frame.shape
            regions = {'full':(0,0,width,height),'center':(width//5,height//10,width*3//5,height*4//5),
                       'left':(0,0,width//2,height),'right':(width//2,0,width-width//2,height)}
            scores = {}
            if previous is not None:
                delta = frame.astype(np.int16)-previous.astype(np.int16)
                adjusted = np.abs(delta-np.median(delta))
                for name,(x,y,w,h) in regions.items():
                    scores[name] = round(float(np.mean(adjusted[y:y+h,x:x+w]>18)*100),3)
            previous = frame
            print(json.dumps({'scores':scores,'warming':count<10}),flush=True)
            count += 1
    finally:
        camera.stop()
        camera.close()
        if running and os.getppid()==parent:
            print(json.dumps({'scan_complete':True}),flush=True)


if __name__ == '__main__':
    try:main()
    except Exception as error:
        print(json.dumps({'error':str(error)}),flush=True)
        sys.exit(1)
