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


# Spotify APIにアクセスするための認証
my_user_id = os.environ.get("USER_ID")
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.environ["CLIENT_ID"],
        client_secret=os.environ["CLIENT_SECRET"],
    )
)


# FIXME: album idを指定して自身のアルバムに追加する関数を追加する
@click.group()
def main():
    pass


@main.command()
@click.option("--id", type=str, help="enter the album ID you want to import")
def import_archive():
    pass


@main.command()
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
        r.write(f"# {playlist.readme}\n")


if __name__ == "__main__":
    main()
