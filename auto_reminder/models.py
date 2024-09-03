# Copyright 2024 Ellis Gibbons
#
# Rose-Hulman Institute of Technology, hereby disclaims all copyright interest
# in the program "auto_reminder" written by Ellis Gibbons.
#
# Dr. Jason Yoder 21 May 2024
# Jason Yoder, Professor
#
# This file is part of auto_reminder.
#
# auto_reminder is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# auto_reminder is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# auto_reminder. If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Callable
import logging

TZ = ZoneInfo("America/Indiana/Indianapolis")
logger = logging.getLogger("auto_reminder")

@dataclass(slots=True, frozen=True)
class Quiz:
    """
    A Moodle quiz. Holds its information and provides some nice formatting and
    a way to check its due date
    """
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
        """
        Creates a quiz from the result of a Moodle API call
        """
        id = quiz["id"]
        name = quiz["name"]
        due_date = datetime.fromtimestamp(quiz["timeclose"], tz=TZ) if quiz["timeclose"] != 0 else None
        return cls(id, name, due_date)

    @classmethod
    def from_file(cls, name: str):
        """
        Creates a quiz from a name obtained in a grades CSV file
        """
        return cls(None, name, None)

    def due_before(self, time: timedelta) -> bool:
        """
        Checks whether the quiz is due within the given timeframe

        :param time: The timeframe to check against
        :return: Whether or not the quiz is due before then
        """
        if self.due_date is None:
            return True # If we don't know the due date, don't filter it out
        epoch = datetime.fromtimestamp(0, tz=TZ)
        now = datetime.now(tz=TZ)
        return self.due_date != epoch and self.due_date < now + time and self.due_date >= now


@dataclass(slots=True)
class Student:
    """
    A student. Holds a list of quizzes that the student has not completed
    """
    id: int
    name: str
    email: str
    missing: list[Quiz] = field(default_factory=list[Quiz]) # TODO: Replace list with set?

    @classmethod
    def from_api(cls, student: dict):
        """
        Creates a student from the result of a Moodle API call
        """
        id = int(student["id"])
        name = student["fullname"]
        email = student["email"]
        return cls(id, name, email)

    @classmethod
    def from_file(cls, student: dict, quizzes: Callable[[], Iterable[Quiz]]):
        """
        Creates a student from a row in a grades CSV file
        """
        id = int(student["ID number"])
        name = student["First name"] + " " + student["Last name"]
        email = student["Email address"]
        missing = [quiz for quiz in quizzes() if student[quiz.name] == "-"]
        return cls(id, name, email, missing)


class QuizFilter(ABC):
    @abstractmethod
    def grade_quiz(quiz: Quiz) -> bool:
        pass


class StudentFinder(ABC):
    """
    Finds students with missing assignments
    """
    config: dict
    threshold: timedelta

    @abstractmethod
    def __init__(self, config):
        self.config = config
        self.threshold = timedelta(days=int(config["threshold"]))

    @abstractmethod
    def get_quizzes(self) -> list[Quiz]:
        """
        Gets all quizzes in a course

        :return: The quizzes
        """
        pass

    @abstractmethod
    def get_students(self) -> list[Student]:
        """
        Gets all students within a course

        :return: The students
        """
        pass

    @abstractmethod
    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        """
        Determines whether or not a student is missing a quiz

        :param student: The student
        :param quiz: The quiz to check for
        :return: Whether or not the student is missing the quiz
        """
        pass

    def get_missing(self) -> list[Student]:
        """
        Gets all students with missing assignments

        :return: The students
        """
        # This is just a default implementation; it won't fit all use cases
        students = self.get_students()
        quizzes = self.get_quizzes()
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(students)
            logger.debug(quizzes)

        for student in students:
            for quiz in quizzes:
                if self.is_missing(student, quiz):
                    logger.debug(f"Student '{student.name}' is missing quiz '{quiz}'")
                    student.missing.append(quiz)

        filtered = filter(lambda student: len(student.missing) > 0, students)
        return list(filtered)
