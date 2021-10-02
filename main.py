import datetime as dt
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import dotenv
import os

### IMPORTANT ###
#Create an app in Spotify and add an app there, you will get the CLIENT ID And Client Secret there.
#Please make sure that you have added redirect_uri as "http://example.com" in spotify website too
#If you are asked to add a url in the console, please add the url which you will get when you will be redirected to 
#the redirect url given above
#If there is any problem, which you might face, please go to SPOTIPY Module Docs and SPOTIFY API Docs too.


# Loads environment variables
dotenv.load_dotenv()

#SECRETS
CLIENT_ID = os.getenv("CLIENTID")
CLIENT_SECRET = os.getenv("CLIENTSECRET")
USERNAME = os.getenv("USERNAME")

date = input("Hey friend! Please tell me the date (YYYY-MM-DD): ")
playlist_name = f"{date} Billboard 100"


def input_date(enter_date):
    """This function converts a given date into the nearest next saturday to that date.
    It is used in url of billboard as billboard only takes saturday"""

    new = dt.datetime.strptime(enter_date, '%Y-%m-%d')
    weekday_original = dt.datetime(year=new.year, month=new.month, day=new.day).weekday()
    weekday_difference = 5 - weekday_original
    if weekday_difference < 0:
        weekday_original = dt.datetime(year=new.year, month=new.month, day=new.day) + dt.timedelta(days=6)
    else:
        weekday_original = dt.datetime(year=new.year, month=new.month, day=new.day) + dt.timedelta(
            days=weekday_difference)
    return weekday_original.strftime("%Y-%m-%d")


# creates songs titles list from billboard
website_url = f"https://www.billboard.com/charts/hot-100/{input_date(date)}"
response = requests.get(url=website_url)
soup = BeautifulSoup(response.text, "html.parser")
title = soup.find_all(name="span", class_="chart-element__information__song")
title_list = [song.text for song in title]

# authenticate spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri="http://example.com", username=USERNAME,
                                               scope="user-library-read, playlist-modify-private, playlist-read-private"))

#add spotify songs uri to songs list
#As these uri are used to add songs in playlist
song_list = []
for song in title:
    try:
        search_song = sp.search(q=song, limit=1)
        song_list.append(search_song["tracks"]["items"][0]["uri"])
    except:
        print(f"error: {search_song}")


#create playlist
create_playlist = sp.user_playlist_create(user=USERNAME, name=playlist_name, 
                                          description=f"Contains the best song on {date}", public=False)

# finds playlist and playlist id
user_playlist = sp.user_playlists(user=USERNAME)
users_playlists_list = [item for item in user_playlist["items"] if item["name"] == playlist_name]
playlist_id = users_playlists_list[0]["id"]

#add songs tp playlist
add_to_playlist = sp.playlist_add_items(playlist_id=playlist_id, items=song_list)

