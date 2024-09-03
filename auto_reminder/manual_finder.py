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

from auto_reminder.models import StudentFinder, Student, Quiz
from collections.abc import Iterable
from functools import partial
import csv

class ManualFinder(StudentFinder):
    """
    Implementation of StudentFinder that gets students from a
    grades CSV file exported from Moodle
    """
    reader: csv.DictReader

    def __init__(self, config: dict, file):
        super().__init__(config)
        self.reader = csv.DictReader(file)

    def get_quizzes(self) -> list[Quiz]:
        quizzes = filter(lambda field: field.startswith("Quiz:"), self.reader.fieldnames)
        quizzes = map(Quiz.from_file, quizzes)
        return list(quizzes)

    def get_students(self) -> list[Student]:
        students = map(partial(Student.from_file, quizzes=self.get_quizzes), self.reader)
        return list(students)

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        return quiz in student.missing

    def get_missing(self) -> Iterable[Student]:
        return filter(lambda student: len(student.missing) > 0, self.get_students())
