import click
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv


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
    # プレイリストの情報を取得
    playlist = sp.playlist(id)

    # 表示
    print(playlist)


if __name__ == "__main__":
    archive_playlist()
