import os
from collections import defaultdict
from dataclasses import dataclass

import spotipy
from dotenv import load_dotenv
from markdown import Markdown
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

load_dotenv()

sp_credential = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
    )
)

sp_oauth = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
        redirect_uri="http://localhost:5000/callback",
        scope="playlist-modify-public playlist-modify-private playlist-read-private",
        cache_path=os.environ["SPOTIPY_CACHE"],
    )
)


@dataclass(frozen=True)
class Playlist:
    id: str
    tracks: list["Track"]
    # collaborative
    description: str
    # external_urls
    # followers
    # href
    # images
    name: str
    owner: "Owner"
    # primary_color
    # public
    # snapshot_id
    # type
    # ur
    url: str

    @classmethod
    def from_playlist_id(cls, playlist_id: int):
        playlist = sp_credential.playlist(playlist_id)
        if not playlist:
            print("playlist not found")
            return None

        # tracks = [Track.from_dict(track) for track in playlist["tracks"]["items"]]
        offset = 0
        limit = 100
        tracks = []
        while True:
            playlist_tracks = sp_credential.playlist_tracks(
                playlist_id, limit=limit, offset=offset
            )
            tracks.extend([Track.from_dict(t) for t in playlist_tracks["items"]])
            if len(playlist_tracks["items"]) < limit:
                break
            offset += limit

        return cls(
            id=playlist["id"],
            owner=Owner.from_dict(playlist["owner"]),
            name=playlist["name"],
            description=playlist["description"],
            tracks=tracks,
            url=playlist["external_urls"].get("spotify"),
        )

    @property
    def readme(self) -> str:
        trakcs = []
        for i, t in enumerate(self.tracks):
            name = f"[{t.name}]({t.url})"
            artists = " & ".join(f"[{a.name}]({a.url})" for a in t.artists)
            album = f"[{t.album.name}]({t.album.url})"
            duration = f"{t.min_and_sec[0]}:{t.min_and_sec[1]}"
            popularity = t.popularity
            trakcs.append(
                f"| {i+1} | {name} | {artists} | {album} | {duration} | {popularity} |"
            )
        traks_text = "\n".join(trakcs)
        title = f"# {self.name}" if not self.name.startswith("# ") else self.name
        sum_duration = sum(t.duration_ms for t in self.tracks)
        sum_duration_m, sum_duration_s = divmod(sum_duration // 1000, 60)

        num_by_artist = defaultdict(int)
        for t in self.tracks:
            for a in t.artists:
                num_by_artist[a] += 1
        primary_artists = [
            a[0]
            for a in sorted(num_by_artist.items(), key=lambda x: x[1], reverse=True)[:3]
        ]

        return f"""{title}
{self.url}

## Description
{self.description}

## Owner
[{self.owner.display_name}]({self.owner.url})

# Statistics
num tracks: {len(self.tracks)}

duration: {sum_duration_m}:{sum_duration_s}

primary artists: {" & ".join(f"[{a.name}]({a.url})" for a in primary_artists)}

## Tracks
| no | Track | Artist | Album | Duration | Popularity |
| -- | ----- | ------ | ----- | -------- | ---------- |
{traks_text}
        """

    @property
    def html(self) -> str:
        md = Markdown()
        return md.convert(self.readme)


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    artists: list["Artist"]
    album: "Album"
    duration_ms: int  # ミリ秒
    popularity: int  # 0-100の値で、そのトラックがどれだけ人気があるかを示す
    url: str

    @classmethod
    def from_dict(cls, track: dict):
        track = track["track"]
        artists = [Artist.from_dict(artist) for artist in track["artists"]]
        return cls(
            id=track["id"],
            name=track["name"],
            artists=artists,
            album=Album.from_dict(track["album"]),
            duration_ms=track["duration_ms"],
            popularity=track["popularity"],
            url=track["external_urls"].get("spotify"),  # ない場合がある
        )

    @property
    def min_and_sec(self) -> tuple[int, int]:
        return divmod(self.duration_ms // 1000, 60)


@dataclass(frozen=True)
class Artist:
    id: str
    name: str
    url: str

    @classmethod
    def from_dict(cls, artist: dict):
        return cls(
            id=artist["id"],
            name=artist["name"],
            url=artist["external_urls"].get("spotify"),  # ない場合がある
        )


@dataclass(frozen=True)
class Album:
    id: str
    images: list["Image"]
    name: str
    release_date: str
    release_date_precision: str  # day, month, year
    artists: list["Artist"]
    url: str
    total_tracks: int

    @classmethod
    def from_dict(cls, album: dict):
        artists = [Artist.from_dict(artist) for artist in album["artists"]]
        images = [Image.from_dict(image) for image in album["images"]]
        return cls(
            id=album["id"],
            images=images,
            name=album["name"],
            release_date=album["release_date"],
            release_date_precision=album["release_date_precision"],
            artists=artists,
            url=album["external_urls"].get("spotify"),  # ない場合がある
            total_tracks=album.get("total_tracks", 0),
        )


@dataclass(frozen=True)
class Image:
    url: str
    width: int
    height: int

    @classmethod
    def from_dict(cls, image: dict):
        return cls(url=image["url"], width=image["width"], height=image["height"])


@dataclass(frozen=True)
class Owner:
    display_name: str
    url: str
    id: str

    @classmethod
    def from_dict(cls, owner: dict):
        return cls(
            display_name=owner["display_name"],
            url=owner["external_urls"].get("spotify"),
            id=owner["id"],
        )


class MyPlaylist:
    def __init__(self):
        self.user_id = os.environ.get("USER_ID")

    def import_playlist(self, playlist: dict):
        # 既に自身のプレイリストに同じ名前のプレイリストがあったら何もしない
        playlists = sp_credential.current_user_playlists()
        if not playlists:
            print("failed to get playlists")
            return
        for p in playlists["items"]:
            if p["name"] == playlist["name"]:
                print(f"playlist {p['name']} already exists")
                return
            if p["id"] == playlist["id"]:
                print(f"playlist {p['id']} already exists")
                return

        new_playlist = sp_credential.user_playlist_create(
            self.user_id, playlist["name"], public=False
        )
        if not new_playlist:
            print("failed to create playlist")
            return
        chunk_size = 100
        track_ids = [track["id"] for track in playlist["tracks"]]
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i : i + chunk_size]
            sp_oauth.user_playlist_add_tracks(
                self.user_id,
                new_playlist["id"],
                chunk,
            )


@dataclass(frozen=True)
class UserPlaylist:
    user_id: str
    playlists: list[Playlist]

    @classmethod
    def from_user_id(cls, user_id: str):
        playlists = sp_credential.user_playlists(user_id)
        if not playlists:
            print("failed to get playlists")
            return None
        return cls(
            user_id=user_id,
            playlists=[Playlist.from_playlist_id(p["id"]) for p in playlists["items"]],
        )
