from vkvideo import VideoApi
import os
import re
import ffmpeg
from datetime import datetime

def get_video_codec(file_path) -> str | None:
    probe = ffmpeg.probe(file_path)
    video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
    if video_streams:
        return video_streams[0]['codec_name']
    else:
        return None

class UploadTask:

    api: VideoApi
    album_id: int
    name: str
    desc: str
    fp: str
    status = "not_uploaded"

    def __init__(self, album_id: int, name: str, desc: str, fp: str, api: VideoApi):
        self.album_id = album_id
        self.name = name
        self.desc = desc
        self.fp = fp
        self.api = api

    def run(self):
        resp = self.api.upload_video(self.name, self.desc, self.album_id, self.fp)
        if("error" in resp):
            self.status = "error"
        else:
            self.status = "success"

class DeleteTask:

    fp: str
    
    def __init__(self, fp):
        self.fp = fp

    def run(self):
        try:
            os.remove(self.fp)
            return True
        except:
            return False

class UploadTaskCreator:

    album_id: int
    album_created = False
    api: VideoApi

    def __init__(self, api):
        self.api = api

    def create_task(self, name: str, dir: str) -> UploadTask | None:
        rfp = os.path.join(dir, name)
        codec_name = None
        try:
            codec_name = get_video_codec(rfp)
        except:
            return None
        if codec_name is None:
            return None
        if not self.album_created:
            self.album_id = self.api.create_album(dir)
            self.album_created = True
        fp = os.path.abspath(rfp)
        cdate = datetime.fromtimestamp(os.stat(rfp).st_ctime)
        sdate = f'Дата создания: {cdate.day}.{cdate.month}.{cdate.year}'
        return UploadTask(self.album_id, os.path.splitext(name)[0], f'{fp}\n{sdate}\nКодек: {codec_name}\n', fp, self.api)

class VideoWorker:

    api: VideoApi
    upload_tasks = dict()
    delete_tasks = dict()

    def __init__(self, api):
        self.api = api

    def handle(self):
        os.chdir("videos")
        for dir in os.listdir():
            for walkdir in os.walk(dir):
                self.handle_dir(walkdir)

    def handle_dir(self, walkdir):
        task_creator = UploadTaskCreator(self.api)
        for file in walkdir[2]:
            if re.match(r'.*\.(avi|mp4|3gp|mpeg|mov|mp3|flv|wmv)$', file):
                task = task_creator.create_task(file, walkdir[0])
                if task is not None:
                    self.upload_tasks[os.path.join(walkdir[0], file)] = task

    def run_upload_tasks(self):
        for task in self.upload_tasks.values():
            if task.status != "success":
                task.run()
        error = False
        for key, task in list(self.upload_tasks.items()):
            print(f'{key}: {task.status}')
            if task.status == "success":
                self.delete_tasks[key] = DeleteTask(task.fp)
                self.upload_tasks.pop(key)
            error = task.status == "error"
        inp = 'n'
        if error:
            inp = input("Do you want to retry upload videos? y/n ")
            if inp == 'y':
                self.run_upload_tasks()
        if inp == 'n':
            if self.delete_tasks:
                for key in self.delete_tasks.keys():
                    print(key)
                inp = input("Do you want to delete these files? y/n ")
                if inp == 'y':
                    for task in self.delete_tasks.values():
                        task.run()





