import json
from threading import Thread
from time import sleep
import unittest

from app import app
import requests

# NOTE: Make sure you run 'pip3 install requests' in your virtualenv

# URL pointing to your local dev host
LOCAL_URL = "http://localhost:5000"

# Sample request bodies
SAMPLE_COURSE = {"code": "CS 1998", "name": "Intro to Backend Development"}
BAD_COURSE = {"name": "Intro to Backend Development"}
SAMPLE_USER = {"name": "Cornell AppDev", "netid": "cad2014"}
BAD_USER = {"name": "Cornell AppDev"}
SAMPLE_ASSIGNMENT = {"title": "PA4", "due_date": 1554076799}
BAD_ASSIGNMENT = {}


# Request endpoint generators
def gen_users_path(user_id=None):
    base_path = f"{LOCAL_URL}/api/users"
    return (
        base_path + "/" if user_id is None else f"{base_path}/{str(user_id)}/"
    )


def gen_courses_path(course_id=None):
    base_path = f"{LOCAL_URL}/api/courses"
    return (
        base_path + "/"
        if course_id is None
        else f"{base_path}/{str(course_id)}/"
    )


# Response handler for unwrapping jsons, provides more useful error messages
def unwrap_response(response, body={}):
    try:
        return response.json()
    except Exception as e:
        req = response.request
        raise Exception(
            f"""
            Error encountered on the following request:

            request path: {req.url}
            request method: {req.method}
            request body: {str(body)}
            exception: {str(e)}

            There is an uncaught-exception being thrown in your
            method handler for this route!
            """
        )


class TestRoutes(unittest.TestCase):
    def test_get_initial_courses(self):
        res = requests.get(gen_courses_path())
        assert res.status_code == 200

    def test_create_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        course = unwrap_response(res)
        assert res.status_code == 201
        assert course["code"] == SAMPLE_COURSE["code"]
        assert course["name"] == SAMPLE_COURSE["name"]
        assert course["assignments"] == []
        assert course["students"] == []
        assert course["instructors"] == []

    def test_create_bad_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(BAD_COURSE))
        assert res.status_code == 400

    def test_get_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.get(gen_courses_path(course_id))
        assert res.status_code == 200
        assert course["id"] == course_id
        assert course["code"] == SAMPLE_COURSE["code"]
        assert course["name"] == SAMPLE_COURSE["name"]
        assert course["assignments"] == []
        assert course["students"] == []
        assert course["instructors"] == []

    def test_delete_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.delete(gen_courses_path(course_id))
        assert res.status_code == 200
        res = requests.get(gen_courses_path(course_id))
        assert res.status_code == 404

    def test_create_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        assert res.status_code == 201
        user = unwrap_response(res)
        assert user["name"] == SAMPLE_USER["name"]
        assert user["netid"] == SAMPLE_USER["netid"]

    def test_create_bad_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(BAD_USER))
        assert res.status_code == 400

    def test_get_user(self):
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        assert res.status_code == 201
        user = unwrap_response(res)
        user_id = user["id"]
        res = requests.get(gen_users_path(user_id))
        assert res.status_code == 200
        user = unwrap_response(res)
        assert user["id"] == user_id
        assert user["name"] == SAMPLE_USER["name"]
        assert user["netid"] == SAMPLE_USER["netid"]
        assert user["courses"] == []

    def test_add_student_to_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        assert res.status_code == 201
        user = unwrap_response(res)
        user_id = user["id"]
        add_user_body = {"type": "student", "user_id": user_id}
        res = requests.post(
            gen_courses_path(course_id) + "add/", data=json.dumps(add_user_body)
        )
        assert res.status_code == 200
        res = requests.get(gen_courses_path(course_id))
        assert res.status_code == 200
        course = unwrap_response(res)
        students = course["students"]
        assert len(students) == 1
        assert students[0]["name"] == SAMPLE_USER["name"]

    def test_add_instructor_to_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.post(gen_users_path(), data=json.dumps(SAMPLE_USER))
        assert res.status_code == 201
        user = unwrap_response(res)
        user_id = user["id"]
        add_user_body = {"type": "instructor", "user_id": user_id}
        res = requests.post(
            gen_courses_path(course_id) + "add/", data=json.dumps(add_user_body)
        )
        assert res.status_code == 200
        res = requests.get(gen_courses_path(course_id))
        assert res.status_code == 200
        course = unwrap_response(res)
        instructors = course["instructors"]
        assert len(instructors) == 1
        assert instructors[0]["name"] == SAMPLE_USER["name"]

    def test_create_assignment_for_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.post(
            gen_courses_path(course_id) + "assignment/",
            data=json.dumps(SAMPLE_ASSIGNMENT),
        )
        assert res.status_code == 201
        assignment = unwrap_response(res)
        assert assignment["title"] == SAMPLE_ASSIGNMENT["title"]
        assert assignment["due_date"] == SAMPLE_ASSIGNMENT["due_date"]

    def test_create_bad_assignment_for_course(self):
        res = requests.post(gen_courses_path(), data=json.dumps(SAMPLE_COURSE))
        assert res.status_code == 201
        course = unwrap_response(res)
        course_id = course["id"]
        res = requests.post(
            gen_courses_path(course_id) + "assignment/",
            data=json.dumps(BAD_ASSIGNMENT),
        )
        assert res.status_code == 400

    def test_get_invalid_course(self):
        res = requests.get(gen_courses_path(1000))
        assert res.status_code == 404

    def test_get_invalid_user(self):
        res = requests.get(gen_users_path(1000))
        assert res.status_code == 404

    def test_add_user_invalid_course(self):
        add_user_body = {"type": "instructor", "user_id": 0}
        res = requests.post(
            gen_courses_path(1000) + "add/", data=json.dumps(add_user_body)
        )
        assert res.status_code == 404

    def test_create_assignment_invalid_course(self):
        res = requests.post(
            gen_courses_path(1000) + "assignment/",
            data=json.dumps(SAMPLE_ASSIGNMENT),
        )
        assert res.status_code == 404


def run_tests():
    sleep(1.5)
    unittest.main()


if __name__ == "__main__":
    thread = Thread(target=run_tests)
    thread.start()
    app.run(host="0.0.0.0", port=5000, debug=False)
