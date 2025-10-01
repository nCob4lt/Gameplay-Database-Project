import re
import requests
from urllib.parse import urlparse, parse_qs

YOUTUBE_API_KEY = "AIzaSyCcgzdpbeZPVU-SWlHoe1sOgqz06lApcpY"

class Tools:

    @staticmethod
    def parse_duration(duration: str) -> int:
        """ Durée type '1h3min2s' -> secondes """
        matches = re.findall(r"(\d+)(h|min|s)", duration)
        total_secs = 0

        for value, unit in matches:
            value = int(value)
            if unit == "h":
                total_secs += value * 3600
            elif unit == "min":
                total_secs += value * 60
            elif unit == "s":
                total_secs += value

        return total_secs
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """ Secondes -> xhyminzs"""
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)

        result = []
        if h: result.append(f"{h}h")
        if m: result.append(f"{m}min")
        if s: result.append(f"{s}s")

        return "".join(result) if result else "0s"
    
    @staticmethod
    def time_adder(*durations: str) -> str:
        """ Ajoute des durées au format str"""
        total_secs = sum(Tools.parse_duration(d) for d in durations)
        return Tools.format_duration(total_secs)
    
    @staticmethod
    def get_youtube_id(url):

        if "youtu.be" in url:
            return url.split("/")[-1]
        
        query = urlparse(url)
        if query.hostname in ["www.youtube.com", "youtube.com"]:
            qs = parse_qs(query.query)
            return qs.get("v", [None])[0]

    @staticmethod  
    def get_youtube_thumbnail(url):
        video_id = Tools.get_youtube_id(url)
        if video_id:
            return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        return None
    
    @staticmethod
    def get_yt_channel_id(url: str):

        parsed = urlparse(url)
        path_parts = parsed.path.strip("/").split("/")

        if "channel" in path_parts:
            return path_parts[-1]

        elif "user" in path_parts:
            username = path_parts[-1]
            api_url = f"https://www.googleapis.com/youtube/v3/channels?part=id&forUsername={username}&key={YOUTUBE_API_KEY}"
            r = requests.get(api_url).json()
            items = r.get("items", [])
            if items:
                return items[0]["id"]

        elif "c" in path_parts:
            custom_name = path_parts[-1]
            api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={custom_name}&key={YOUTUBE_API_KEY}"
            r = requests.get(api_url).json()
            items = r.get("items", [])
            if items:
                return items[0]["snippet"]["channelId"]

        return None
    
    @staticmethod
    def get_youtube_pp(channel_id: str):
        channel_api = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
        channel_data = requests.get(channel_api).json()
        avatar_url = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        return avatar_url
        