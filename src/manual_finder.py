from models import StudentFinder, Student, Quiz
from collections.abc import Iterable
from functools import partial
import csv

class ManualFinder(StudentFinder):
    reader: csv.DictReader

    def __init__(self, config: dict, file):
        super().__init__(config)
        self.reader = csv.DictReader(file)

    def get_quizzes(self) -> Iterable[Quiz]:
        quizzes = filter(lambda field: field.startswith("Quiz:"), self.reader.fieldnames)
        return map(Quiz.from_file, quizzes)

    def get_students(self) -> Iterable[Student]:
        return map(partial(Student.from_file, quizzes=self.get_quizzes), self.reader)

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        return quiz in student.missing

    def get_missing(self) -> Iterable[Student]:
        return filter(lambda student: len(student.missing) > 0, self.get_students())
