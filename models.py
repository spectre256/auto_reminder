from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime, timedelta

@dataclass
class Quiz:
    id: int
    name: str
    due_date: datetime | None

    def __str__(self):
        return "{}, due {:%m/%d %I:%M %p}".format(self.name, self.due_date)

    @classmethod
    def from_api(cls, quiz: dict):
        id = quiz["id"]
        name = quiz["name"]
        due_date = datetime.utcfromtimestamp(quiz["timeclose"]) if quiz["timeclose"] != 0 else None
        return cls(id, name, due_date)

    def due_before(self, time: timedelta) -> bool:
        epoch = datetime.utcfromtimestamp(0)
        return self.due_date != epoch and self.due_date < datetime.utcnow() + time and self.due_date >= datetime.utcnow()


@dataclass
class Student:
    id: int
    name: str
    email: str
    missing: List[Quiz] = field(default_factory=List[Quiz])

    @classmethod
    def from_api(cls, student: dict):
        id = student["id"]
        name = student["fullname"]
        email = student["email"]
        return cls()

class StudentFinder(ABC):
    config: dict
    threshold: timedelta

    @abstractmethod
    def __init__(self, config):
        self.config = config
        self.threshold = timedelta(days=int(config["threshold"]))

    @abstractmethod
    def get_quizzes(self) -> List[Quiz]:
        pass

    @abstractmethod
    def get_students(self) -> List[Student]:
        pass

    @abstractmethod
    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        pass

    def get_missing(self) -> List[Student]:
        students = get_students()
        quizzes = get_quizzes()

        for student in students:
            for quiz in quizzes:
                if is_missing(student, quiz):
                    student.missing.append(quiz)

        return students
