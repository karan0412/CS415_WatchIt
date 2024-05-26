import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Movie, Booking

def get_recommendations(user):
    # Fetch all movies and bookings
    movies = Movie.objects.all()
    bookings = Booking.objects.filter(user=user)

    if not movies.exists() or not bookings.exists():
        return Movie.objects.none()

    # Extract data from user's bookings
    booking_data = []
    for booking in bookings:
        movie = booking.movie
        tags = ', '.join([tag.name for tag in movie.tags.all()])
        booking_data.append({
            'id': movie.id,
            'title': movie.title,
            'tags': tags,
            'director': movie.director if movie.director else '',
            'starring': movie.starring if movie.starring else ''
        })

    if not booking_data:
        return Movie.objects.none()

    booking_df = pd.DataFrame(booking_data)
    booking_df['combined_features'] = booking_df['tags'] + ' ' + booking_df['director'] + ' ' + booking_df['starring']

    # Debug: Print booking data
    print("Booking Data:\n", booking_df)

    # Create a DataFrame for all movies
    data = []
    for movie in movies:
        tags = ', '.join([tag.name for tag in movie.tags.all()])
        data.append({
            'id': movie.id,
            'title': movie.title,
            'tags': tags,
            'director': movie.director if movie.director else '',
            'starring': movie.starring if movie.starring else ''
        })

    df = pd.DataFrame(data)
    df['combined_features'] = df['tags'] + ' ' + df['director'] + ' ' + df['starring']

    # Debug: Print all movies data
    print("All Movies Data:\n", df)

    # Vectorize the combined features
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['combined_features'])

    # Vectorize the booking features
    booking_tfidf_matrix = tfidf.transform(booking_df['combined_features'])

    # Calculate cosine similarity between bookings and all movies
    cosine_sim = cosine_similarity(booking_tfidf_matrix, tfidf_matrix)

    # Debug: Print cosine similarity matrix
    print("Cosine Similarity Matrix:\n", cosine_sim)

    # Get the indices of the movies the user has booked
    user_movie_ids = set(bookings.values_list('movie_id', flat=True))
    similar_movies = set()

    for idx in range(cosine_sim.shape[0]):
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[:3]  # Get top similar movies

        for i in sim_scores:
            movie_id = df['id'].iloc[i[0]]
            if movie_id not in user_movie_ids:
                similar_movies.add(movie_id)

    if not similar_movies:
        print("No similar movies found")
        return Movie.objects.none()

    recommended_movies = Movie.objects.filter(id__in=similar_movies)[:3]

    # Debug: Print recommended movies
    print("Recommended Movies:\n", recommended_movies)

    return recommended_movies
