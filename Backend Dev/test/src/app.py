import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(body, status_code=200):
    return json.dumps(body), status_code

def failure_response(message, status_code = 404):
    return json.dumps({"error": message}), status_code

@app.route("/")
@app.route("/tasks/")
def get_tasks():
    return success_response({"task": DB.get_tasks()})

@app.route("/tasks/", methods = ["POST"])
def create_task():
    body = json.loads(request.data)
    description = body.get("description")
    task_id = DB.create_task(description, False)
    return success_response(DB.get_task_by_id(task_id), 201)

@app.route("/tasks/")
def get_task(task_id):
    task = DB.get_tasks_by_id(task_id)
    if task is None:
        return failure_response("Task Not Found!")
    return success_response(task)    

def get_all_subtasks():
    pass

def get_subtask_from_task():
    #get task and its id. then get the subtask (subtask has id of task id)
    #instead of running "SELECT * FROM task WHERE ID = ?", (id,), do "SELECT * FROM task WHERE TASK_ID = ?", (task_id,)
    #endpoint to get task is /tasks/<int:task_id>/
    #endpoint to get subtask is /tasks/<int:task_id>/subtasks/<int:subtask_id>/
    pass

def get_subtask_from_id():
    pass


def hello_world():
    return "Hello world!"


# your routes here


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
