from models import StudentFinder, Student, Quiz
from datetime import datetime, timedelta
from collections.abc import Iterable
from functools import partial
from moodle import Moodle

class ApiFinder(StudentFinder):
    courseid: int
    roleid: int
    api: Moodle

    def __init__(self, config: dict):
        super().__init__(config)

        self.courseid = config["course_id"]
        self.roleid = config["role_id"]
        self.api = Moodle(config["url"], config["token"])

    def get_quizzes(self) -> Iterable[Quiz]:
        quizzes = moodle("mod_quiz_get_quizzes_by_courses", courseids=[self.courseid])["quizzes"]
        quizzes = map(Quiz.from_api, quizzes)
        return filter(partial(Quiz.due_before, time=self.threshold), quizzes)

    def get_students(self) -> Iterable[Student]:
        users = moodle("core_enrol_get_enrolled_users", courseid=self.courseid)
        students = filter(lambda user: any((role["roleid"] == self.roleid for role in user["roles"])), users)
        return map(Student.from_api, students)

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        result = moodle("mod_quiz_get_user_best_grade", userid=student.id, quizid=quiz.id)
        return result["hasgrade"] # TODO: Threshold for grade?
