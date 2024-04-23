from moodle import Moodle
from json import dump
from datetime import datetime, timedelta

# url = "https://sandbox.moodledemo.net/webservice/rest/server.php"
url = "https://moodle.rose-hulman.edu/webserver/rest/server.php"
token = "SECRET TOKEN GOES HERE"
courseid = 106360
# student_roleid = 5
time_threshold = timedelta(days=7)

moodle = Moodle(url, token)

quizzes = moodle("mod_quiz_get_quizzes_by_courses", courseids=[courseid])
users = moodle("core_enrol_get_enrolled_users", courseid=courseid)

for quiz in quizzes["quizzes"]:
    # Skip quizzes due later than the threshold and already due
    timeclose = datetime.utcfromtimestamp(quiz["timeclose"])
    if quiz["timeclose"] != 0 and (timeclose > datetime.utcnow() + time_threshold or timeclose < datetime.utcnow()):
        print("Skipped quiz '" + quiz["name"] + "'")
        continue

    print("Quiz '" + quiz["name"] + "' is due " + str(timeclose))
    for user in users:
        # Skip teachers
        # if not any((role["roleid"] == student_roleid for role in user["roles"])):
        #     print(f"Skipping teacher '" + user["fullname"] + "'")
        #     continue

        result = moodle("mod_quiz_get_user_best_grade", userid=user["id"], quizid=quiz["id"])
        print("User '" + user["fullname"] + "' has " + ("" if result["hasgrade"] else "not ") + "completed quiz '" + quiz["name"] + "' with role " + str(user["roles"][0]["roleid"]))

    print()
