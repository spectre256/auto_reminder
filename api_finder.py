import models
from typing import List
from datetime import datetime, timedelta
from moodle import Moodle

class ApiFinder(StudentFinder):
    courseid: int
    threshold: timedelta
    api: Moodle

    def __init__(self, config: dict):
        super().__init__(self, config)

        self.courseid = config["COURSE_ID"]
        self.api = Moodle(config["URL"], config["TOKEN"])

    def get_quizzes(self) -> List[Quiz]:
        quizzes = moodle("mod_quiz_get_quizzes_by_courses", courseids=[self.courseid])["quizzes"]
        return list(map(Quiz.from, quizzes)) # TODO: Filter by time close

    def get_students(self) -> List[Student]:
        students = moodle("core_enrol_get_enrolled_users", courseid=self.courseid)
        return list(map(Student.from, students)) # TODO: Filter out teachers

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        result = moodle("mod_quiz_get_user_best_grade", userid=student.id, quizid=quiz.id)
        return result["hasgrade"] # TODO: Threshold for grade?
