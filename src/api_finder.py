from models import *
from typing import List
from datetime import datetime, timedelta
from functools import partial
from moodle import Moodle

class ApiFinder(StudentFinder):
    threshold: timedelta
    courseid: int
    roleid: int
    api: Moodle

    def __init__(self, config):
        super().__init__(self, config)

        self.courseid = config["course_id"]
        self.roleid = config["role_id"]
        self.api = Moodle(config["url"], config["token"])

    def get_quizzes(self) -> List[Quiz]:
        quizzes = moodle("mod_quiz_get_quizzes_by_courses", courseids=[self.courseid])["quizzes"]
        quizzes = map(Quiz.from_api, quizzes)
        quizzes = filter(partial(Quiz.due_before, time=self.threshold), quizzes)
        return list(quizzes)

    def get_students(self) -> List[Student]:
        users = moodle("core_enrol_get_enrolled_users", courseid=self.courseid)
        students = filter(lambda user: any((role["roleid"] == self.roleid for role in user["roles"])), users)
        return list(map(Student.from_api, students))

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        result = moodle("mod_quiz_get_user_best_grade", userid=student.id, quizid=quiz.id)
        return result["hasgrade"] # TODO: Threshold for grade?
