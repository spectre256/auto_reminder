from models import StudentFinder, Student, Quiz
import csv

class ManualFinder(StudentFinder):
    reader: csv.DictReader

    def __init__(self, config: dict, file):
        super().__init__(self, config)
        reader = csv.DictReader(file)

    def get_quizzes(self) -> list[Quiz]:
        quizzes = filter(lambda field: field.startswith("Quiz:"), self.reader.fieldnames)
        quizzes = map(Quiz.from_file, quizzes)
        return list(quizzes)

    def get_students(self) -> list[Student]:
        students = map(Student.from_file, self.student_reader)
        return list(students)

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        return quiz.name in student.missing
