from celery import Celery
import os
import subprocess

celery_app = Celery('tasks', broker='redis://localhost:6379/0')

@celery_app.task
def combine_videos(video_files):
    input_filenames = []
    for i, video_data in enumerate(video_files):
        input_filename = f"/tmp/input_{i}.mp4"
        with open(input_filename, "wb") as f:
            f.write(video_data)
        input_filenames.append(input_filename)
    
    output_filename = f"static/{combine_videos.request.id}.mp4"
    command = ["ffmpeg"]
    for input_filename in input_filenames:
        command.extend(["-i", input_filename])
    command.extend(["-filter_complex", "concat=n=3:v=1:a=1", output_filename])
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        raise Exception(f"FFmpeg failed: {e}")
    finally:
        for input_filename in input_filenames:
            os.remove(input_filename)
    
    return output_filename
