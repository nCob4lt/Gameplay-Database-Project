"""

File: tools.py

Description: This module provides various utility functions used throughout the Gameplay Database bot.

It includes:
- Time parsing and formatting helpers
- YouTube URL parsing and data fetching utilities
- Moderator permission checking for Discord interactions

External dependencies:
    - requests (for YouTube API calls)
    - discord.py (for Discord interactions)
    - re, os, json, urllib, pathlib

Author: cobalt

"""

# --- Standard imports ---
import re
import requests
from urllib.parse import urlparse, parse_qs
import os
import discord
import json
from pathlib import Path

# --- Local imports ---
from exceptions.custom_exceptions import *
from utilities.applogger import AppLogger

# --- Global setup ---
YOUTUBE_API_KEY = os.getenv("GPDB_YT_API_KEY")
applogger = AppLogger()

# -------------------- TIME UTILITIES --------------------

def parse_duration(duration: str) -> int:

    """

    Converts a duration string like '1h3min2s' into total seconds.

    Parameters
    ----------
    duration : str
        A duration string (e.g., '2h5min30s').

    Returns
    -------
    int
        Total number of seconds represented by the duration.

    """

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

def format_duration(seconds: int) -> str:

    """

    Converts a number of seconds into a formatted duration string.

    Parameters
    ----------
    seconds : int
        Total seconds.

    Returns
    -------
    str
        Duration string in the format "XhYminZs".
        Examples:
            3661 -> "1h1min1s"
            120  -> "2min"

    """

    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)

    result = []
    if h: result.append(f"{h}h")
    if m: result.append(f"{m}min")
    if s: result.append(f"{s}s")

    return "".join(result) if result else "0s"

def time_adder(*durations: str) -> str:

    """

    Adds multiple duration strings together.

    Parameters
    ----------
    *durations : str
        Any number of duration strings (e.g., '2min30s', '1h').

    Returns
    -------
    str
        Total duration as a formatted string (e.g., "1h2min30s").

    """

    total_secs = sum(parse_duration(d) for d in durations)
    return format_duration(total_secs)

# -------------------- YOUTUBE UTILITIES --------------------

def get_youtube_id(url):

    """

    Extracts the YouTube video ID from a YouTube URL.

    Supports:
        - Standard YouTube links (e.g. 'https://www.youtube.com/watch?v=abc123')
        - Shortened links (e.g. 'https://youtu.be/abc123')

    Parameters
    ----------
    url : str
        The YouTube video URL.

    Returns
    -------
    str | None
        The extracted video ID, or None if not found.

    """

    if "youtu.be" in url:
        return url.split("/")[-1]
    
    query = urlparse(url)
    if query.hostname in ["www.youtube.com", "youtube.com"]:
        qs = parse_qs(query.query)
        return qs.get("v", [None])[0]
 
def get_youtube_thumbnail(url):

    """

    Returns the thumbnail URL for a given YouTube video.

    Parameters
    ----------
    url : str
        YouTube video URL.

    Returns
    -------
    str | None
        Thumbnail URL, or None if no video ID could be extracted.

    """

    video_id = get_youtube_id(url)
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return None

def get_yt_channel_id(url: str):

    """

    Retrieves a YouTube channel ID from a given channel URL.

    Supports various URL types:
        - /channel/<id>
        - /user/<username>
        - /c/<custom_name>

    Parameters
    ----------
    url : str
        YouTube channel URL.

    Returns
    -------
    str | None
        The channel ID, or None if it could not be determined.

    Notes
    -----
    This function uses the YouTube Data API v3 for resolving custom and user URLs.
    Requires a valid API key in the environment variable `GPDB_YT_API_KEY`.

    """

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

def get_youtube_pp(channel_id: str):

    """

    Fetches a YouTube channel's profile picture (high quality).

    Parameters
    ----------
    channel_id : str
        The YouTube channel ID.

    Returns
    -------
    str
        URL of the channel's profile image.

    """

    channel_api = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={YOUTUBE_API_KEY}"
    channel_data = requests.get(channel_api).json()
    avatar_url = channel_data["items"][0]["snippet"]["thumbnails"]["high"]["url"]
    return avatar_url

async def check_mod(interaction: discord.Interaction):

    """

    Checks if a Discord user is authorized as a moderator.

    Loads a JSON file containing a whitelist of moderator user IDs.
    If the user is not found, a response is sent and an exception is raised.

    Parameters
    ----------
    interaction : discord.Interaction
        The current Discord interaction context.

    Raises
    ------
    MissingModPermissions
        If the user is not found in the whitelist.

    Side Effects
    ------------
    - Sends an ephemeral message to the user if unauthorized.
    - Logs an error through AppLogger.

    """

    json_file = Path(__file__).parent.parent.parent / "mod/mod_whitelist.json"
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    if interaction.user.id not in data.get("mods", []):
        applogger.error(f" Unauthorized user {interaction.user.name} tried to use mod command {interaction.command.name} (user was not found in the whitelist)")
        raise MissingModPermissions("Interaction user was not found in the mod whitelist")

        