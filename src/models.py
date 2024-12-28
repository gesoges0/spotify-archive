from dataclasses import dataclass

from markdown import Markdown


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
    def from_playlist_dict(cls, playlist: dict):
        tracks = [Track.from_dict(track) for track in playlist["tracks"]["items"]]
        return cls(
            id=playlist["id"],
            owner=Owner.from_dict(playlist["owner"]),
            name=playlist["name"],
            description=playlist["description"],
            tracks=tracks,
            url=playlist["external_urls"]["spotify"],
        )

    @property
    def readme(self) -> str:
        trakcs = []
        for i, t in enumerate(self.tracks):
            name = f"[{t.name}]({t.url})"
            artists = " & ".join(f"[{a.name}]({a.url})" for a in t.artists)
            album = f"[{t.album.name}]({t.album.url})"
            duration = f"{t.min_and_sec[0]}分{t.min_and_sec[1]}秒"
            popularity = t.popularity
            trakcs.append(
                f"| {i+1} | {name} | {artists} | {album} | {duration} | {popularity} |"
            )
        traks_text = "\n".join(trakcs)
        title = f"# {self.name}" if not self.name.startswith("# ") else self.name
        return f"""{title}
{self.url}

## Description
{self.description}

## Owner
[{self.owner.display_name}]({self.owner.url})

## Tracks
{len(self.tracks)} tracks

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
            url=track["external_urls"]["spotify"],
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
