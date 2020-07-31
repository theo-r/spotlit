import os

import streamlit as st
import spotipy
import pandas as pd

from streamlit.server.Server import Server

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session_id_key

def prep_tracks_data(data):
    df = pd.DataFrame(data)
    df = pd.json_normalize(df['items'])
    df['rank'] = df.index
    df = df.explode('artists').reset_index(drop=True)
    artists = pd.json_normalize(df.artists)
    artists = artists.rename(columns={name: 'artists.'+ name for name in artists.columns})
    df = pd.concat([artists, df], axis=1)
    aggs_dict = {name: create_aggs_dict(name) for name in df.columns}
    df = df.groupby('name').agg(aggs_dict).sort_values('rank').reset_index(drop=True)
    return df

def prep_artists_data(data):
    df = pd.DataFrame(data)
    df = pd.json_normalize(df['items'])
    df['rank'] = df.index
    return df

def string_agg(series): return series.str.cat(sep=' + ')

def create_aggs_dict(name):
    if name == 'artists.name':
        return string_agg
    else:
        return 'first'

urlPara = None
token = None

sessions = Server.get_current()._session_info_by_id
session_id_key = list(sessions.keys())[0]
session = sessions[session_id_key]

st.title('Your top tracks and artists')
scope = 'user-top-read'
auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=session_cache_path(), scope=scope)

auth_url = auth_manager.get_authorize_url()
st.markdown(f'[Log in to Spotify]({auth_url})')

try:
    urlPara = session.ws.request.connection.params.urlpara
except AttributeError:
    urlPara = None

try:
    token = auth_manager.get_access_token(urlPara['code'])
except TypeError:
    token = None

if token is not None:
    
    # Step 4. Signed in, display data
    sp = spotipy.Spotify(auth_manager=auth_manager)

    @st.cache(allow_output_mutation=True)
    def prepare_data():
        tracks_short = prep_tracks_data(sp.current_user_top_tracks(limit=50, time_range='short_term'))
        tracks_medium = prep_tracks_data(sp.current_user_top_tracks(limit=50, time_range='medium_term'))
        tracks_long = prep_tracks_data(sp.current_user_top_tracks(limit=50, time_range='long_term'))

        artists_short = prep_artists_data(sp.current_user_top_artists(limit=50, time_range='short_term'))
        artists_medium = prep_artists_data(sp.current_user_top_artists(limit=50, time_range='medium_term'))
        artists_long = prep_artists_data(sp.current_user_top_artists(limit=50, time_range='long_term'))

        artists_short.rename(columns={'name': 'short_term'}, inplace=True)
        artists_medium.rename(columns={'name': 'medium_term'}, inplace=True)
        artists_long.rename(columns={'name': 'long_term'}, inplace=True)

        artists = pd.concat([artists_short, artists_medium, artists_long], axis=1)

        return tracks_short, tracks_medium, tracks_long, artists

    tracks_short, tracks_medium, tracks_long, artists = prepare_data()

    st.write('Top tracks (short-term)')
    st.write(tracks_short[['name', 'artists.name', 'album.name']][:25])

    st.write('Top tracks (medium-term)')
    st.write(tracks_medium[['name', 'artists.name', 'album.name']][:25])

    st.write('Top tracks (long-term)')
    st.write(tracks_long[['name', 'artists.name', 'album.name']][:25])

    st.write('Top artists')
    st.write(artists[['short_term', 'medium_term', 'long_term']][:25])