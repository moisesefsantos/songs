# songs
Top 5 billboard songs of 1958-2025 with a spotify link to hear them

HOW TO USE: ACSESS THIS LINK https://developer.spotify.com/ TO ENSURE YOU HAVE A DEVEOLPER ACCOUNT IN SPOTIFY. IT IS NECESSARY TO ALLOW YOU SHOW THE LINKS OF SONGS. CREATE AN ACCOUNT IN CASE IF YOU DO NOT HAVE ONE AND GO TO DASHBOARD SECTION. CREATE AN APP, FEEL FREE TO CHOOSE THE NAME AND DESCRIPTION, IT DOESN'T MATTER AT ALL. IN REDIRECT URL USE THIS http://localhost:8501/. IT IS THE DEFAULT STREAMLIT LOCAL PORT.

This app allows you to find the top 5 billboard songs between august of 1958 and february of 2025, the code is made of the following parts:
Initial Configuration – Sets up the necessary libraries and Streamlit page settings.
Session State Management – Stores Spotify connection status in Streamlit’s session state.
Helper Functions – Cleans song titles and artist names, initializes the Spotify client, and searches for Spotify links.
Fetching Top Songs – Filters the Billboard dataset to get the top 5 songs for a selected month and year.
Sidebar Menu – Allows users to enter Spotify API credentials and select a time period for the rankings.
Loading Billboard Data – Reads the CSV file containing Billboard rankings and processes the date column.
Displaying Rankings – Shows the top 5 songs in a structured format with titles, artists, and positions.
Spotify Integration – Searches for and displays Spotify links if the connection is active.
Error Handling – Displays messages if there is an issue loading data or connecting to Spotify.
