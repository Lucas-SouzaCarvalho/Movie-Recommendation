import requests

# Replace with your base URL and movie ID
base_url = 'http://localhost:8000/recommendations/similarity/'
movie_id = 2279042  # Replace with the ID of a movie in your database

# Send the GET request
response = requests.get(f'{base_url}{movie_id}/')

# Check the response status code
if response.status_code == 200:
  # Get the JSON response data
  data = response.json()
  
  # Print the first 3 recommendations (modify as needed)
  for i in range(3):
    movie = data[i]
    print(f"Recommended Movie ID: {movie['id']}")
    print(f"Similarity Score: {movie['similarity_score']}")
    print("-" * 30)  # Separator for readability
else:
  print(f"Error: {response.status_code}")
