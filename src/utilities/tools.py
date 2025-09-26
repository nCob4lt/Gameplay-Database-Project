import re
from urllib.parse import urlparse, parse_qs

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