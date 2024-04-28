from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

@dataclass(slots=True)
class Quiz:
    id: int | None
    name: str
    due_date: datetime | None

    def __str__(self):
        if self.due_date is None:
            return self.name
        else:
            return "{}, due {:%m/%d %I:%M %p}".format(self.name, self.due_date)

    @classmethod
    def from_api(cls, quiz: dict):
        id = quiz["id"]
        name = quiz["name"]
        due_date = datetime.utcfromtimestamp(quiz["timeclose"]) if quiz["timeclose"] != 0 else None
        return cls(id, name, due_date)

    @classmethod
    def from_file(cls, name: str):
        return cls(None, name, None)

    def due_before(self, time: timedelta) -> bool:
        if self.due_date is None:
            return True # If we don't know the due date, don't filter it out
        epoch = datetime.utcfromtimestamp(0)
        return self.due_date != epoch and self.due_date < datetime.utcnow() + time and self.due_date >= datetime.utcnow()


@dataclass(slots=True)
class Student:
    id: int
    name: str
    email: str
    missing: list[Quiz] = field(default_factory=list[Quiz])

    @classmethod
    def from_api(cls, student: dict):
        id = student["id"]
        name = student["fullname"]
        email = student["email"]
        return cls(id, name, email)

    @classmethod
    def from_file(cls, student: dict):
        id = student["ID number"]
        name = student["First name"] + " " + student["Last name"]
        email = student["Email address"]
        return cls(id, name, email)

class StudentFinder(ABC):
    config: dict
    threshold: timedelta

    @abstractmethod
    def __init__(self, config):
        self.config = config
        self.threshold = timedelta(days=int(config["threshold"]))

    @abstractmethod
    def get_quizzes(self) -> list[Quiz]:
        pass

    @abstractmethod
    def get_students(self) -> list[Student]:
        pass

    @abstractmethod
    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        pass

    def get_missing(self) -> list[Student]:
        students = get_students()
        quizzes = get_quizzes()

        for student in students:
            for quiz in quizzes:
                if is_missing(student, quiz):
                    student.missing.append(quiz)

        return students
