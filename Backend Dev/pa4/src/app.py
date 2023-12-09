from db import db
from db import Students
from db import Instructors
from db import User
from db import Course
from db import Assignments
from flask import Flask, request
import json


app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

def success_response(body, status_code=200):
    return json.dumps(body), status_code

def failure_response(message, status_code = 404):
    return json.dumps({"error": message}), status_code

# your routes here
@app.route("/api/courses/")
def get_courses():
    return success_response({"courses": [c.serialize() for c in Course.query.all()]})

@app.route("/api/courses/", methods=["POST"])
def create_course():
    body = json.loads(request.data)
    if body.get("code") is None or body.get("name") is None:
        return failure_response("No Code or Name", 400)
    new_course = Course(code=body.get("code"), name=body.get("name"))
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)

@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())

@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def add_assignment(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    body = json.loads(request.data)
    if body.get("title") is None or body.get("due_date") is None:
        return failure_response("No Title or Due Date", 400)
    new_assignment = Assignments(
        title=body.get("title"),
        due_date=body.get("due_date"),
        course_id = course_id
    )
    temp = {"id":course_id, "code":course.code, "name":course.name}
    db.session.add(new_assignment)
    db.session.commit()
    response = new_assignment.serialize()
    response['courses'] = temp
    return success_response(response, 201)

@app.route("/api/users/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    if body.get("name") is None or body.get("netid") is None:
        return failure_response("No Name or Netid", 400)
    new_user = User(name=body.get("name"), netid=body.get("netid"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())

@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def assign_users(course_id):
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    body=json.loads(request.data)
    user_id=body.get("user_id")
    type=body.get("type")
    user=User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    name = user.name
    if type == "student":
        new_student = Students(
            user_id=user_id,
            name = name,
            courses = course
        )
        course.students.append(new_student)
        db.session.add(new_student)
        db.session.commit()
    elif type == "instructor":
        new_instructor = Instructors(
            user_id=user_id,
            name = name,
            courses=course
        )
        course.instructors.append(new_instructor)
        db.session.add(new_instructor)
        db.session.commit()
    return success_response(course.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
