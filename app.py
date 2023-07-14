# Imports
import streamlit as st
import pandas as pd  # for data handling
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity  # for recommendation

def main():
    # Load and preprocess the data
    songs_df = pd.read_csv('./data/demo_data.csv')

    # Add custom CSS to change the background color and style
    st.markdown(
        """
        <style>
            body {
                background-color: #2a2747;
                padding: 20px;
            }
            
            .main-container {
                background-color: #f5f5f5;
                padding: 20px;
                border-radius: 10px;
            }
            
            .poppins-font {
                font-family: 'Poppins', sans-serif;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Create a title for the app
    st.markdown(
        """
        <h1 style="color: #d5f979; font-family: 'Poppins', sans-serif;">Song Recommendation System</h1>
        """,
        unsafe_allow_html=True
    )

    # Enclose the main content in a div with the 'main-container' class
    with st.container() as main_container:
        # Update the lines to use the 'poppins-font' class
        st.markdown(
            '<div class="poppins-font">by James Meredith</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="poppins-font">Select a song from the list to receive custom recommendations based on the mood you are in.</div>',
            unsafe_allow_html=True
        )

    # Create sidebar widgets for song selection and mood
    selected_song = st.sidebar.selectbox('Select a song:', [f"{title} by {artist_name}" for title, artist_name in zip(songs_df['title'], songs_df['artist_name'])])
    mood = st.sidebar.selectbox('What kind of mood are you in:', ['happy', 'sad', 'chill', 'angry'])
    button_clicked = st.sidebar.button("Get recommendations")

    # Extract song title from the selected song
    selected_song_title = selected_song.split(' by ')[0]
    selected_song_artist = selected_song.split(' by ')[1]

    if button_clicked:
        # Filter songs based on mood
        filtered_songs = songs_df[songs_df['mood'] == mood]

        # Filter the selected song
        song_features = songs_df.loc[songs_df['title'] == selected_song_title, filtered_songs.select_dtypes(include='number').columns].values

        if filtered_songs.empty:
            st.write(f"No songs available for the selected mood: {mood}")
        else:
            # Apply StandardScaler to song features
            scaler = StandardScaler()
            scaled_features = scaler.fit_transform(filtered_songs.select_dtypes(include='number'))

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(song_features, scaled_features)

            # Get indices of similar songs
            similar_songs_indices = similarity_matrix.argsort()[0][-11:-1]

            # Get the recommended songs
            recommended_songs = filtered_songs.iloc[similar_songs_indices]

            # Filter the recommended songs for uniqueness
            recommended_songs_unique = recommended_songs.drop_duplicates(subset=['title'])

            # Check if the number of unique songs is less than 10
            if len(recommended_songs_unique) < 10:
                # Add more similar songs until 10 unique songs are obtained
                additional_indices = similarity_matrix.argsort()[0][-20:-1]
                additional_songs = filtered_songs.iloc[additional_indices]
                additional_songs_unique = additional_songs.drop_duplicates(subset=['title'])
                recommended_songs_unique = pd.concat([recommended_songs_unique, additional_songs_unique]).drop_duplicates(subset=['title'])

                # Trim the recommendations to 10 unique songs
                recommended_songs_unique = recommended_songs_unique.head(10)

            # Display recommendations
            st.write(f"**If you liked '{selected_song_title}' by '{selected_song_artist}', here are some songs you're sure to enjoy:**")
            recommended_songs_with_index = recommended_songs_unique[['title', 'artist_name']].reset_index(drop=True)
            recommended_songs_with_index.columns = ['Title', 'Artist']
            recommended_songs_with_index.index += 1
            st.table(recommended_songs_with_index)

if __name__ == '__main__':
    main()