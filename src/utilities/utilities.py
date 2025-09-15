import re

class DatabaseUtilities:

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
        total_secs = sum(DatabaseUtilities.parse_duration(d) for d in durations)
        return DatabaseUtilities.format_duration(total_secs)