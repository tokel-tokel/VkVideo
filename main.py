import videoworker
import vkvideo
from dotenv import load_dotenv
import os

load_dotenv()

api = vkvideo.VideoApi(os.getenv("token"), int(os.getenv("group_id")))
viwo = videoworker.VideoWorker(api)
viwo.handle()
viwo.run_upload_tasks()
