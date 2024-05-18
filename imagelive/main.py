from fastapi import FastAPI, BackgroundTasks
from vidgear.gears  import CamGear
import cv2
from fastapi.responses import StreamingResponse

app = FastAPI()

this_urls="https://www.youtube.com/watch?v=3LXQWU67Ufk"


@app.get("/stream/")
async def stream_video(background_tasks: BackgroundTasks):
    url = this_urls

    # Start the video stream in the background
    background_tasks.add_task(start_video_stream, url)

    return {"message": "Video stream started"}

def generate_frames(url):
    stream = CamGear(source=url, stream_mode=True, logging=True).start()

    while True:
        frame = stream.read()

        if frame is None:
            break

        print(frame)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cv2.destroyAllWindows()

@app.get("/video_feed/")
async def video_feed():
    url = this_urls
    return StreamingResponse(generate_frames(url), media_type="multipart/x-mixed-replace; boundary=frame")

def start_video_stream(url):
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)