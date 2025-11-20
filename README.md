# Gameplay Database

A discord bot to manage creators, layouts, collabs and musics for Geometry Dash

---

## Features

- Commands to register infos about creators, layouts, collabs, musics and artists
- Commands to fetch infos about creators, collabs, musics and artists
- Request registration system to submit data to the database

## How it works 

- The Gameplay Database has 5 tables which contains the attributes of the following objects : creator, layout, collab, music, artist

### Table creator

- id (The ID of the creator in the database (also primary key))
- username (Creator's username)
- nationality (Creator's nationality)
- discord (Creator's discord)
- discord_uid (The discord ID of the creator)
- yt (Link to creator's youtube channel)
- layouts_registered (The amount of layouts from the creator registered in the database)
- collab_participations (The amount of collabs the creator participated to)
- total_time_built (The total length of the all the layouts built by the creator end to end)
- registration_date (The date when the registration was executed)
- recorder_name (The name of the user who registered the entry)

---

### Table layout

- id (The ID of the layout in the database — primary key)
- creator_id (The ID of the creator who built the layout — foreign key to creator)
- creator_name (Name of the creator who built the layout)
- type (Type/category of the layout)
- name (Layout name — required)
- length (Length of the layout)
- yt (YouTube link associated with the layout)
- music_id (ID of the associated music entry — foreign key to music)
- music_ngid (Newgrounds ID of the song used)
- music_name (Name of the song used for the layout)
- music_artist (Artist of the song used)
- igid (In-game ID of the layout, if applicable)
- registration_date (Date when the layout was registered)
- recorder_name (Name of the user who registered the entry)
- recorder_notes (Extra notes written by the recorder)
- artist_id (ID of the artist linked to this layout — foreign key to artist)
- masterlevel_id (ID of the referenced collab/masterlevel — foreign key to collab)
- masterlevel (Name of the referenced masterlevel, if any)

Note : If a layout is a **collab** part, the masterlevel is the level the part belongs to.

---

### Table collab

- id (The ID of the collab in the database — primary key)
- host_id (ID of the host of the collab — foreign key to creator)
- host_name (Username of the collab host)
- name (Name of the collab)
- builders_number (Total number of builders involved)
- length (Length of the collab)
- yt (YouTube link associated with the collab)
- music_id (ID of the associated music entry — foreign key to music)
- music_ngid (Newgrounds ID of the song used)
- music_name (Name of the song used)
- music_artist (Artist of the song used)
- igid (In-game ID of the collab, if applicable)
- registration_date (Date when the collab was registered)
- recorder_name (Name of the user who registered the entry)
- recorder_notes (Notes written by the recorder)
- artist_id (ID of the artist linked to the collab — foreign key to artist)

---

### Table music

- id (The ID of the song in the database — primary key)
- name (Name of the song — required)
- artist (Name of the artist who produced the music)
- length (Length of the song)
- type (Type/category of the song)
- yt (YouTube link for the track)
- soundcloud (SoundCloud link for the track)
- uses (Number of times the song is used across layouts and collabs)
- ngid (Newgrounds ID of the song)
- registration_date (Date when the song entry was registered)
- recorder_name (Name of the user who registered the entry)
- recorder_notes (Notes written by the recorder)
- artist_id (ID of the music artist — foreign key to artist)

---

### Table artist

- id (The ID of the artist in the database — primary key)
- name (Name of the artist — unique, required)
- yt (Link to the artist’s YouTube channel)
- soundcloud (Link to the artist’s SoundCloud page)
- songs_registered (Number of songs from this artist registered in the database)
- total_song_uses (Total number of times songs by this artist have been used)
- registration_date (Date when the artist entry was registered)
- recorder_name (Name of the user who registered the entry)
- recorder_notes (Notes written by the recorder)

## Precautions to take before submitting recordings

- When registering infos, make sure to respect the case of writing, because when retrieving infos, the bot will not found anything but the exact same name as registered.
- Before registering object, check beforehand it does not already exist in the database
- When registering, try to fill in (if you can) all the optional informations
- When registering a collab, do not forget to register all the collab parts that belongs to it afterwards, or vice versa
- Images are found by YouTube API, try to fill them all the time.
- If you just want to complete the database, check for missing references with /missing and add them.

---

## Synchronization

During the synchronization process, the database will attempt to update statistics and retrieve any missing information across all tables.
If certain data cannot be resolved automatically, the bot will log it into a file.
The /missing command will then read this file and display all unresolved or incomplete entries.

---

## Commands

### 📝 Retrieving object

- `/get_artist_by_name` — Retrieve an artist by name  
- `/get_collab_by_name` — Retrieve a collab by name  
- `/get_creator_by_discord` — Retrieve a creator by Discord username  
- `/get_creator_by_name` — Retrieve a creator by name  
- `/get_layout_by_name` — Retrieve a layout by name  
- `/get_music_by_name` — Retrieve a music by name  
- `/get_random_layout` — Retrieve a random layout from the database  

### 📋 Retrieving list of objects

- `/layouts_from` — List layouts from a creator  
- `/layouts_with` — List layouts using a specific music or artist  
- `/levels_from` — List layouts and collabs from a creator  
- `/levels_with` — List all levels (layouts + collabs) using a music or artist  
- `/collabs_from` — List collabs from a creator  
- `/collabs_with` — List collabs using a specific music or artist  
- `/musics_from` — List musics registered from an artist  
- `/parts_from` — List parts created by a creator  
- `/parts_of` — List parts associated with a layout or collab  

### 🛠 Registration requests

- `/request_artist` — Request the registration of an artist  
- `/request_collab` — Request the registration of a collab  
- `/request_creator` — Request the registration of a creator  
- `/request_layout` — Request the registration of a layout  
- `/request_music` — Request the registration of a music

### 🛠 Update requests

- `/request_update_creator` — Request the update of a creator entry
- `/request_update_layout` — Request the update of a layout entry
- `/request_update_collab` — Request the update of a collab entry
- `/request_update_music` — Request the update of a music entry
- `/request_update_artist` — Request the update of a artist entry

### ℹ️ General

- `/about` — Information about the bot  
- `/missing` — Show missing references in the database  
- `/database_stats` — Show statistics about the database

---

## Installation

- [Invitation link](https://discord.com/oauth2/authorize?client_id=1409139926196555936&permissions=8&integration_type=0&scope=applications.commands+bot)

---

## Contributing

Feel free to dm me in discord to request suggestions or modifications (vncobalt_). 

---

## Other

- Version : 1.0.0
- Python version : 3.11.4
- Discord.py : 2.4.0
- Author : Cobalt

---

## License

This project is licensed under the MIT License — see the LICENSE file for details.

