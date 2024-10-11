import requests
import json

class VkApiError(Exception):
    pass

class VideoApi:

    token: str
    public_id: int
    owner_id = 0

    def __init__(self, token: str, id: int):
        self.token = token
        self.public_id = id

    def create_album(self, name: str) -> int:
        r = requests.post(f"https://api.vk.com/method/video.addAlbum?access_token={self.token}&group_id={self.public_id}&title={name}&v=5.199")
        resp = json.loads(r.text)
        if "error" in resp:
            raise VkApiError()
        return resp['response']['album_id'] 

    def upload_video(self, name: str, desc: str, album_id: int, fp: str):
        r = requests.post(f"https://api.vk.com/method/video.save?access_token={self.token}&group_id={self.public_id}&name={name}&description={desc}&album_id={album_id}&v=5.199")
        resp = json.loads(r.text)
        if "error" in resp:
            return resp
        upload_url = resp['response']['upload_url']
        params = {'access_token': self.token, 'v': 5.199}
        files = {'video_file': open(fp, 'rb')}
        r = requests.post(upload_url, params=params, files=files)
        try:
            resp = json.loads(r.text)
        except:
            return {"error": "error"}
        return resp

