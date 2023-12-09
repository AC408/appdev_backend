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
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/users/")
def get_users():
    return success_response({"users": DB.get_users()})

@app.route("/api/users/", methods = ["POST"])
def create_user():
   body = json.loads(request.data)
   name = body.get("name", "none")
   username = body.get("username", "none")
   balance = body.get("balance", 0)
   id = DB.create_user(name, username, balance)
   return success_response(DB.get_users_by_id(id), 201)

@app.route("/api/user/<int:id>/")
def get_user(id):
    user = DB.get_users_by_id(id)
    if user is None:
        return failure_response("User Not Found!")
    return success_response(user)

@app.route("/api/user/<int:id>/", methods = ["DELETE"])
def del_user(id):   
    user = DB.delete_user(id)
    if user is None:
        return failure_response("User Not Found!")
    return success_response(user)
    
#change this to transactions
@app.route("/api/transactions/", methods = ["POST"])
def create_transaction():
    body = json.loads(request.data)
    sender_id = body.get("sender_id", None)
    receiver_id = body.get("receiver_id", None)
    amount = body.get("amount", None)
    message = body.get("message", None)
    accepted = body.get("accepted", None)
    if(sender_id is None):
        return failure_response("No Sender_id Given", 400)
    if(receiver_id is None):
        return failure_response("No Receiver_id Given", 400)
    if(amount is None):
        return failure_response("No Amount Given", 400)
    id = DB.create_transaction(sender_id, receiver_id, amount, message, accepted)
    if id is None:
        return failure_response("Balance Not Enough", 403)
    return success_response(DB.get_transactions_by_id(id), 201)

@app.route("/api/transaction/<int:id>/", methods = ["POST"])
def manage_transaction(id):
    body = json.loads(request.data)
    accepted = body.get("accepted", None)
    id = DB.manage_transaction(id,accepted)
    if id is None:
        return failure_response("Cannot Change Accepted Field If Transaction Has Already Been Accepted/Denied", 403)
    return success_response(DB.get_transactions_by_id(id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
