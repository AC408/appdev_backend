import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

tasks = {
    0: {
        "id": 0,
        "description": "do laundry",
        "done": False
    },
    1: {
        "id": 1,
        "description": "do the dishes",
        "done": False
    },
}
task_id_counter = 2

@app.route("/")
def hello_world():
    return "Hello world!"

@app.route("/tasks/")
def get_all_tasks():
    response = {
        "tasks": list(tasks.values())
    }
    return json.dumps(response), 200

@app.route("/tasks/", methods=["POST"])
def create_task():
    global task_id_counter
    body = json.loads(request.data)
    description = body.get("description", "none")
    response = {
        "id": task_id_counter,
        "description": description,
        "done": False
    }
    tasks[task_id_counter] = response
    task_id_counter += 1
    return json.dumps(response), 201


@app.route("/tasks/<int:task_id>/")
def get_specific_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    return json.dumps(task), 200

@app.route("/tasks/<int:task_id>/", methods=['POST'])
def update_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    body = json.loads(request.data)
    task["description"] = body.get("description", task["description"])
    task["done"] = body.get("done", task["done"])
    return json.dumps(task), 200

@app.route("/tasks/<int:task_id>/", methods=['DELETE'])
def delete_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return json.dumps({"error": "Task not found"}), 404
    del tasks[task_id]
    return json.dumps(task), 200

# your routes here


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
