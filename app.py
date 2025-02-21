import streamlit as st
import pandas as pd
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# Page config
st.set_page_config(
    page_title="Billboard Top Songs",
    page_icon="🎵",
    layout="wide"
)

# Initialize session state
if 'spotify' not in st.session_state:
    st.session_state.spotify = None
if 'spotify_connected' not in st.session_state:
    st.session_state.spotify_connected = False

# Title
st.title("🎵 Billboard Top Songs")

def clean_song_title(title):
    """Clean song title by removing common features text and special characters"""
    # Remove text in parentheses or brackets
    title = re.sub(r'\([^)]*\)', '', title)
    title = re.sub(r'\[[^\]]*\]', '', title)
    
    # Remove 'feat.', 'ft.', 'featuring' and following text
    title = re.sub(r'(?i)feat\..*$', '', title)
    title = re.sub(r'(?i)ft\..*$', '', title)
    title = re.sub(r'(?i)featuring.*$', '', title)
    
    # Remove special characters and extra spaces
    title = re.sub(r'[^\w\s-]', '', title)
    title = ' '.join(title.split())
    
    return title.strip()

def clean_artist_name(artist):
    """Clean artist name by removing common additions and special characters"""
    # Remove text in parentheses or brackets
    artist = re.sub(r'\([^)]*\)', '', artist)
    artist = re.sub(r'\[[^\]]*\]', '', artist)
    
    # Remove special characters and extra spaces
    artist = re.sub(r'[^\w\s-]', '', artist)
    artist = ' '.join(artist.split())
    
    return artist.strip()

def initialize_spotify_client(client_id, client_secret):
    """Initialize Spotify client with credentials"""
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        st.session_state.spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        # Test the connection with a simple search
        st.session_state.spotify.search(q='test', limit=1)
        st.session_state.spotify_connected = True
        return True
    except Exception as e:
        st.error(f"Failed to connect to Spotify: {str(e)}")
        st.session_state.spotify = None
        st.session_state.spotify_connected = False
        return False

def search_spotify_link(title, artist):
    """Search for a song on Spotify and return its URL using multiple search strategies"""
    if not st.session_state.spotify_connected:
        return None
    
    try:
        # Clean the title and artist
        clean_title = clean_song_title(title)
        clean_artist = clean_artist_name(artist)
        
        # Search strategies in order of precision
        search_strategies = [
            f"track:{clean_title} artist:{clean_artist}",  # Exact match
            f"{clean_title} {clean_artist}",              # Simple search
            f"\"{clean_title}\" {clean_artist}",          # Exact title match
            clean_title,                                  # Just the title
        ]
        
        for query in search_strategies:
            results = st.session_state.spotify.search(q=query, type='track', limit=10)
            
            if results['tracks']['items']:
                # Try to find the best match
                for track in results['tracks']['items']:
                    track_title = clean_song_title(track['name'].lower())
                    track_artist = clean_artist_name(track['artists'][0]['name'].lower())
                    
                    # Check if either title matches exactly or artist matches exactly
                    if (clean_title.lower() in track_title or track_title in clean_title.lower()) and \
                       (clean_artist.lower() in track_artist or track_artist in clean_artist.lower()):
                        return track['external_urls']['spotify']
                
                # If no good match found, return the first result
                return results['tracks']['items'][0]['external_urls']['spotify']
                
    except Exception as e:
        st.error(f"Error searching Spotify: {str(e)}")
    return None

def get_top_songs(df, month, year):
    # Convert chart_week to datetime if it's not already
    df['chart_week'] = pd.to_datetime(df['chart_week'])
    
    # Filter by month and year
    mask = (df['chart_week'].dt.month == month) & (df['chart_week'].dt.year == year)
    filtered_df = df[mask]
    
    if filtered_df.empty:
        return None
    
    # Get the last week of the specified month
    last_week = filtered_df['chart_week'].max()
    
    # Get top 5 songs for the last week of the month
    top_songs = filtered_df[filtered_df['chart_week'] == last_week].head(5)
    
    return top_songs

# Spotify credentials in sidebar
with st.sidebar:
    st.header("Spotify API Credentials")
    
    # Create columns for better layout
    cred_col1, cred_col2 = st.columns(2)
    
    with cred_col1:
        client_id = st.text_input("Client ID", type="password")
    with cred_col2:
        client_secret = st.text_input("Client Secret", type="password")
    
    # Add connect button
    if st.button("Connect to Spotify"):
        if client_id and client_secret:
            if initialize_spotify_client(client_id, client_secret):
                st.success("Successfully connected to Spotify! 🎉")
        else:
            st.error("Please enter both Client ID and Client Secret")
    
    # Show connection status
    if st.session_state.spotify_connected:
        st.success("Connected to Spotify ✓")
    else:
        st.warning("Not connected to Spotify")
    
    st.header("Select Time Period")

# Load the data
try:
    df = pd.read_csv('billboards.csv')
    df['chart_week'] = pd.to_datetime(df['chart_week'])
    
    # Get available years from the data
    years = sorted(df['chart_week'].dt.year.unique())
    
    # Year and month selection
    with st.sidebar:
        selected_year = st.selectbox("Select Year", years)
        selected_month = st.selectbox("Select Month", range(1, 13), 
                                    format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
    
    # When user selects a time period
    if selected_year and selected_month:
        top_songs = get_top_songs(df, selected_month, selected_year)
        
        if top_songs is not None:
            st.header(f"Top 5 Songs - {datetime(2000, selected_month, 1).strftime('%B')} {selected_year}")
            
            # Display each song in a card-like format
            for i, song in top_songs.iterrows():
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"""
                        ### {i+1}. {song['title']}
                        **Artist:** {song['performer']}  
                        **Current Position:** #{song['current_week']}
                        """)
                    with col2:
                        if st.session_state.spotify_connected:
                            spotify_link = search_spotify_link(song['title'], song['performer'])
                            if spotify_link:
                                st.link_button("Listen on Spotify 🎵", spotify_link)
                            else:
                                st.write("*Song not found on Spotify*")
                        else:
                            st.info("Connect to Spotify to enable links")
                    st.markdown("---")
        else:
            st.error("No data available for the selected time period.")
            
except FileNotFoundError:
    st.error("Error: Could not find 'billboards.csv' file in the current directory. Please make sure the file exists and is named correctly.")
