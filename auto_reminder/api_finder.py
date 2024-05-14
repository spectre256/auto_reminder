from auto_reminder.models import StudentFinder, Student, Quiz
from datetime import datetime, timedelta
from collections.abc import Iterable
from functools import partial
from moodle import Moodle
import logging

logger = logging.getLogger("auto_reminder")

class ApiFinder(StudentFinder):
    """
    Implementation of StudentFinder that uses the Moodle API
    to get students
    """
    courseid: int
    roleid: int
    api: Moodle

    def __init__(self, config: dict):
        super().__init__(config)

        self.courseid = config["course_id"]
        self.roleid = config["role_id"]
        self.api = Moodle(config["url"], config["token"])

    def get_quizzes(self) -> list[Quiz]:
        quizzes = self.api("mod_quiz_get_quizzes_by_courses", courseids=[self.courseid])["quizzes"]
        quizzes = map(Quiz.from_api, quizzes)
        quizzes = filter(partial(Quiz.due_before, time=self.threshold), quizzes)
        logger.debug("Called get_quizzes")
        return list(quizzes)

    def get_students(self) -> list[Student]:
        users = self.api("core_enrol_get_enrolled_users", courseid=self.courseid)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("All students: %s", users)
        students = filter(lambda user: any((role["roleid"] == self.roleid for role in user["roles"])), users)
        students = map(Student.from_api, students)
        logger.debug("Called get_students")
        return list(students)

    def is_missing(self, student: Student, quiz: Quiz) -> bool:
        result = self.api("mod_quiz_get_user_best_grade", userid=student.id, quizid=quiz.id)
        logger.debug(f"Result for student '{student.name}' and quiz '{quiz}': {result}")
        return not result["hasgrade"] # TODO: Threshold for grade?
