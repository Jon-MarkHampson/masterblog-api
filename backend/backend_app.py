import os
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

POSTS_PATH = os.path.join(os.path.dirname(__file__), 'posts.json')
SWAGGER_URL = "/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"  # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


def load_posts():
    """Load posts from the JSON file."""
    try:
        with open(POSTS_PATH, 'r') as handle:
            return json.load(handle)
    except FileNotFoundError:
        return []
    
def save_posts(posts):
    """Save posts to the JSON file."""
    try:
        with open(POSTS_PATH, 'w') as handle:
            json.dump(posts, handle, indent=4)
    except Exception as e:
        print(f"Error saving posts: {e}")

@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    """ Handle GET and POST requests for posts.
    GET: Returns all posts, optionally sorted by a specified field.
    POST: Creates a new post with the provided data.
    """
    
    # Load posts from file instead of relying on a global variable.
    posts = load_posts()
    if request.method == 'POST':
        new_post = request.get_json()
        if not new_post or not new_post.get("title") or not new_post.get("content") or not new_post.get("author") or not new_post.get("date"):
            return jsonify({"error": "Invalid post data"}), 400
        
        # Validate and convert the date field
        try:
            parsed_date = datetime.strptime(new_post['date'], "%Y-%m-%d")
            new_post['date'] = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400
        
        new_post['id'] = len(posts) + 1
        # Initialize likes to 0
        new_post['likes'] = 0  
        posts.append(new_post)
        save_posts(posts)
        return jsonify(new_post), 201

    # GET: Handle optional sorting
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')
    posts_to_return = posts.copy()

    if sort_field:
        if sort_field not in ['title', 'content', 'author', 'date']:
            return jsonify({"error": "Invalid sort field. Allowed fields: title, content, author, date."}), 400
        if direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid direction. Allowed values: asc, desc."}), 400
        reverse = direction == 'desc'
        posts_to_return = sorted(posts_to_return, key=lambda post: post.get(sort_field, ""), reverse=reverse)

    return jsonify(posts_to_return)

@app.route('/api/posts/<int:post_id>/like', methods=['GET'])
def like_post(post_id):
    """Like a post by its ID.
    Increments the likes count for the specified post."""
    
    posts = load_posts()
    post_to_like = next((post for post in posts if post['id'] == post_id), None)
    if post_to_like is None:
        return jsonify({"error": f"No post found with id {post_id}"}), 404
    
    # Increment the likes count
    post_to_like['likes'] = post_to_like.get('likes', 0) + 1
    save_posts(posts)
    return jsonify(post_to_like), 200


@app.route('/api/posts/<int:post_id>', methods=['DELETE', 'PUT'])
def handle_posts(post_id):
    """Handle PUT and DELETE requests for a specific post by its ID.
    PUT: Updates the post with the provided data.
    DELETE: Deletes the post with the specified ID."""
    
    # Load posts from file instead of relying on a global variable.
    posts = load_posts()
    post_to_update = next((post for post in posts if post['id'] == post_id), None)
    if post_to_update is None:
        return jsonify({"error": f"No post found with id {post_id}"}), 404
    
    if request.method == 'PUT':
        updated_data = request.get_json()
        if not updated_data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in updated_data:
            post_to_update['title'] = updated_data['title']
        if 'content' in updated_data:
            post_to_update['content'] = updated_data['content']
        if 'author' in updated_data:
            post_to_update['author'] = updated_data['author']
        if 'date' in updated_data:
            try:
                parsed_date = datetime.strptime(updated_data['date'], "%Y-%m-%d")
                post_to_update['date'] = parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                return jsonify({"error": "Invalid date format. Expected YYYY-MM-DD"}), 400

        save_posts(posts)
        return jsonify(post_to_update), 200
    
    elif request.method == 'DELETE':      
        posts = [post for post in posts if post['id'] != post_id]
        save_posts(posts)
        return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """ Search for posts based on query parameters.
    Supports searching by title, content, author, and date."""
    
    # Load posts from file instead of relying on a global variable.
    posts = load_posts()
    title_query = request.args.get('title', '')
    content_query = request.args.get('content', '')
    author_query = request.args.get('author', '')
    date_query = request.args.get('date', '')
    
    # If no query parameters are provided, return all posts
    if not title_query and not content_query and not author_query and not date_query:
        return jsonify(posts)
    
    filtered_posts = [
        post for post in posts
        if (title_query and title_query.lower() in post['title'].lower()) or
           (content_query and content_query.lower() in post['content'].lower()) or
           (author_query and author_query.lower() in post['author'].lower()) or
           (date_query and date_query.lower() in post['date'].lower())
    ]
    
    return jsonify(filtered_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
