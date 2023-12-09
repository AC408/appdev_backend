import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    0: {
        "id": 0,
        "upvotes": 1,
        "title": "My cat is the cutest!",
        "link": "https://i.imgur.com/jseZqNK.jpg",
        "username": "alicia98"
    },
    1: {
        "id": 1,
        "upvotes": 3,
        "title": "Cat loaf",
        "link": "https://i.imgur.com/TJ46wX4.jpg",
        "username": "alicia98"
    },
}

comments = {
    0: {
        "id": 0,
        "upvotes": 8,
        "text": "Wow, my first Reddit gold!",
        "username": "alicia98"
    },
    1: {
        "id": 1,
        "upvotes": 1,
        "text": "Test",
        "username": "dog123"
    },
}

linked_comments = {
    0: {
        "post id": 0,
        "id": 0,
        "upvotes": 8,
        "text": "Wow, my first Reddit gold!",
        "username": "alicia98"
    },
    1: {
        "post id": 0,
        "id": 1,
        "upvotes": 1,
        "text": "Test",
        "username": "dog123"
    },
}

post_counter = 2
comment_counter = 2

@app.route("/api/posts/")
def get_all_posts():
    response = {
        "posts": list(posts.values())
    }
    return json.dumps(response), 200
    
@app.route("/api/posts/", methods=["POST"])
def create_post():
    global post_counter
    body = json.loads(request.data)
    title = body.get("title", "none")
    link = body.get("link", "none")
    username = body.get("username", "none")
    response = {
        "id": post_counter,
        "upvotes": 1,
        "title": title,
        "link": link,
        "username": username
    }
    posts[post_counter] = response
    post_counter += 1
    return json.dumps(response), 201

@app.route("/api/posts/<int:post_id>/")
def get_specific_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/", methods=['DELETE'])
def delete_post(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    del posts[post_id]
    return json.dumps(post), 200

@app.route("/api/posts/<int:post_id>/comments/")
def get_all_comments(post_id): # error is that when a comment is added to a post, the comment  returned for that post is the first comment at index 0
    comment_id = {}
    local_id = 0
    response_vals = {}
    id_found = False
    for key in linked_comments: #key gives the entire collections of "actual" attributes
        for keys in linked_comments[key].keys(): #keys gives "actual" attributes: id, upvote, title, etc
            if(keys == "post id"): #if the attribute is on post id and they are equal
                if(linked_comments[key]["post id"] == post_id):
                    comment_id[local_id] = linked_comments[key]["id"] #return comment id
                    local_id += 1
    local_id = 0
    for key in comments:
        for keys in comment_id: #gives the collections of "actual" attributes
            if(comments[key]["id"] == comment_id[keys]): #if the comment id are the same
                response_vals[local_id] = comments[key]
                local_id += 1
                id_found =  True
    if not id_found:
        return json.dumps({"error": "Comment not found"}), 404
    response = {
        "comments": list(response_vals.values())
    }
    return json.dumps(response), 200

@app.route("/api/posts/<int:post_id>/comments/", methods=["POST"])
def create_comment(post_id):
    post = posts.get(post_id)
    if not post:
        return json.dumps({"error": "Post not found"}), 404
    global comment_counter
    body = json.loads(request.data)
    text = body.get("text", "none")
    username = body.get("username", "none")
    response = {
        "id": comment_counter,
        "upvotes": 1,
        "text": text,
        "username": username
    }
    comments[comment_counter] = response
    response_linked = {
        "post id": post_id,
        "id": comment_counter,
        "upvotes": 1,
        "text": text,
        "username": username
    }
    linked_comments[comment_counter] = response_linked
    comment_counter += 1
    return json.dumps(response), 201

@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>/", methods=['POST'])
def update_comment(post_id, comment_id):
    comment = comments.get(comment_id)
    if not comment:
        return json.dumps({"error": "Comment not found"}), 404
    body = json.loads(request.data)
    comment["text"] = body.get("text", comment["text"])
    comment = linked_comments.get(comment_id)
    if not comment:
        return json.dumps({"error": "Comment not found"}), 404
    body = json.loads(request.data)
    comment["text"] = body.get("text", comment["text"])
    return json.dumps(comment), 200


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
