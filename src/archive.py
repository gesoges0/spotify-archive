import json
import os
import pprint
from dataclasses import asdict
from pathlib import Path

import click
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

from models import Playlist

load_dotenv()


my_user_id = os.environ.get("USER_ID")

# Spotify APIにアクセスするための認証
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
    )
)


@click.command()
@click.option("--id", type=str, help="enter the playlist ID youo want to archive")
def archive_playlist(id: str):

    playlist = Playlist.from_playlist_dict(sp.playlist(id))
    pprint.pprint(asdict(playlist))
    dir = Path(f"archive/albums/{playlist.owner.id}")
    json_path = dir / f"{playlist.id}.json"
    readme_path = dir / "README.md"
    if not dir.exists():
        dir.mkdir(parents=True, exist_ok=True)
    with json_path.open("w") as j, readme_path.open("w") as r:
        json.dump(asdict(playlist), j, indent=2, ensure_ascii=False)
        r.write(f"# {playlist.name}\n")


if __name__ == "__main__":
    archive_playlist()
