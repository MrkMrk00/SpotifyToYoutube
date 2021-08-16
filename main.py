import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


def main():
    # vypíná https (I guess)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    spotify_user_id = ''
    yt_playlist_id = ''
    sp_playlist_name = ''
    client_secret_credentials = ''
    start_song_index = 0
    playlists: dict[str, list[str]] = {}

    # spotify init, innit?
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id='',
            client_secret=''
        )
    )

    # vytvoř instanci YT API clienta
    # google init, innit?
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file=client_secret_credentials,
        scopes=["https://www.googleapis.com/auth/youtube.force-ssl"]
    )
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        serviceName='youtube',
        version='v3',
        credentials=credentials
    )

    # ukradni playlisty uživatele na spotify a výtáhni názvy songů
    for pl in sp.user_playlists(spotify_user_id)['items']:
        ofs = 0
        songs = []
        # nefunguje jim limit, tak se to prostě spojí do jednoho seznamu pomocí offsetu
        # nejdřív to jede od 0, pokud je ten playlist delší než 100, tak to jede znovu od 100 -> 200 (limit je 100)
        while True:
            songs += (sp.playlist_items(playlist_id=pl['id'], offset=ofs)['items'])
            if (len(songs)+ofs) % 100 == 0:
                ofs += 100
            else:
                break

        # dict na songy {'nazev playlistu': ['nazev songu', ...], ...}
        playlists[pl['name']] = []
        for item in songs:
            track = item['track']
            playlists[pl['name']].append(track['artists'][0]['name'] + ' ' + track['name'])

    for pl in playlists:
        print(pl)

    # range ve spotify playlistu
    # od který songy přidávat
    # search stojí 100, playlistItems().insert() stojí 50; dohromady je denní max 10 000 u jednoho projektu
    for i in range(start_song_index, len(playlists[sp_playlist_name])):
        print(playlists[sp_playlist_name][i])
        # vyhledá písničku podle názvu
        # vezme první video z výsledků a uloží do proměnné id videa
        res = youtube.search().list(
                part='snippet',
                maxResults=1,
                q=playlists[sp_playlist_name][i],
                type='video'
            ).execute()['items'][0]['id']
        print(res)

        # vloží do playlistu s danym ID písničku s ID v res
        youtube.playlistItems().insert(
            part='snippet',
            body={
                'snippet': {
                    'playlistId': yt_playlist_id,
                    'position': 0,
                    'resourceId': res
                }
            }
        ).execute()


if __name__ == '__main__':
    main()
