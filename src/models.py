from dataclasses import dataclass


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

    @classmethod
    def from_playlist_dict(cls, playlist: dict):
        tracks = [Track.from_dict(track) for track in playlist["tracks"]["items"]]
        return cls(
            id=playlist["id"],
            owner=Owner.from_dict(playlist["owner"]),
            name=playlist["name"],
            description=playlist["description"],
            tracks=tracks,
        )


@dataclass(frozen=True)
class Track:
    id: str
    name: str
    artists: list["Artist"]
    album: "Album"
    duration_ms: int
    popularity: int

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
        )


@dataclass(frozen=True)
class Artist:
    id: str
    name: str
    url: str

    @classmethod
    def from_dict(cls, artist: dict):
        return cls(
            id=artist["id"], name=artist["name"], url=artist["external_urls"]["spotify"]
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
            url=album["external_urls"]["spotify"],
            total_tracks=album["total_tracks"],
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
            url=owner["external_urls"]["spotify"],
            id=owner["id"],
        )
