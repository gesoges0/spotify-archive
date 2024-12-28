import glob
import json
from dataclasses import asdict
from pathlib import Path

import click
from dotenv import load_dotenv

from models import MyPlaylist, Playlist, UserPlaylist

load_dotenv()


@click.group()
def main():
    pass


@main.command()
@click.option("--id", type=str, help="enter the playlist ID you want to import")
def import_playlist_archive(id: str):
    # Get Archive Playlist
    dirs = glob.glob(f"archive/playlists/*/{id}")
    if not dirs:
        print("No such playlist archive")
        return
    dir = Path(dirs[0])
    json_path = dir / "output.json"
    with json_path.open("r") as j:
        playlist = json.load(j)

    # Import Playlist
    my_playlist = MyPlaylist()
    my_playlist.import_playlist(playlist)

    pass


def _archive_playlist(id: str):
    playlist = Playlist.from_playlist_id(id)
    dir = Path(
        f"archive/playlists/{playlist.owner.display_name}_{playlist.owner.id}/{playlist.id}"
    )
    json_path = dir / "output.json"
    readme_path = dir / "README.md"
    if not dir.exists():
        dir.mkdir(parents=True, exist_ok=True)
    with json_path.open("w") as j, readme_path.open("w") as r:
        json.dump(asdict(playlist), j, indent=2, ensure_ascii=False)
        r.write(f"{playlist.readme}\n")


@main.command()
@click.option("--id", type=str, help="enter the playlist ID youo want to archive")
def archive_playlist(id: str):
    _archive_playlist(id)


@main.command()
@click.option("--id", type=str, help="enter the user ID you want to archive")
def archive_user(id: str):
    playlists: list[Playlist] = UserPlaylist.from_user_id(id).playlists
    for i, playlist in enumerate(playlists):
        print(i, playlist.name, playlist.id)
        _archive_playlist(playlist.id)


if __name__ == "__main__":
    main()
