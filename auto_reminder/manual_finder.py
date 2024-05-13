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
