from functools import cached_property
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# your classes here
association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("students_id",db.Integer, db.ForeignKey("students.id"))
)

association_table_2 = db.Table(
    "association_2",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("instructors_id", db.Integer, db.ForeignKey("instructors.id"))
)

class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignments", cascade="delete")
    instructors = db.relationship("Instructors", secondary=association_table_2,back_populates="courses")
    students = db.relationship("Students", secondary=association_table,back_populates="courses")

    def __init__(self, **kwargs):
        self.code = kwargs.get("code")
        self.name = kwargs.get("name")

    def serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize() for a in self.assignments],
            "instructors": [i.sub_serialize() for i in self.instructors],
            "students": [s.sub_serialize() for s in self.students]
        }

    def sub_serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize() for a in self.assignments],
        }

class Assignments(db.Model):
    __tablename__ = "assignments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.due_date = kwargs.get("due_date")
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "due_date": self.due_date,
        }

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.Integer, nullable=False)
    courses = db.relationship("Students", cascade="delete")
    courses = db.relationship("Instructors", cascade="delete")

    def _init_(self, **kwargs):
        self.name = kwargs.get("name")
        self.netid = kwargs.get("netid")


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [c.cserialize() for c in self.courses]
        }

class Students(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    courses = db.relationship("Course", secondary=association_table, back_populates="students")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.name = kwargs.get("name")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "courses": [c.sub_serialize() for c in self.courses]
        }

    def cserialize(self):
        return [c.sub_serialize() for c in self.courses]

    def sub_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }

class Instructors(db.Model):
    __tablename__ = "instructors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    courses = db.relationship("Course", secondary=association_table_2, back_populates="instructors")

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.name = kwargs.get("name")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id,
            "courses": [c.sub_serialize() for c in self.courses]
        }

    def cserialize(self):
        return [c.sub_serialize() for c in self.courses]

    def sub_serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "user_id": self.user_id
        }
