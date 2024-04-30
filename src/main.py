from models import StudentFinder
from api_finder import ApiFinder
from manual_finder import ManualFinder
from emailer import Emailer
import argparse
import json
import sys
import os
from string import Template


class App:
    config: dict
    student_finder: StudentFinder
    emailer: Emailer

    def __init__(self):
        args = App.parse_args(sys.argv[1:]) # The [1:] skips the first argument which is the filename

        if args["config"]:
            self.config = json.load(args["config"])
        else:
            self.config = os.environ

        if args["api"]:
            self.student_finder = ApiFinder(self.config)
        elif args["manual"]:
            self.student_finder = ManualFinder(self.config, args["manual"])

        self.emailer = Emailer(self.config)

    def run(self):
        students = self.student_finder.get_missing()
        # print(list(students))
        template = Template(self.config["template"])
        # print(self.emailer.compose(template, next(students)))
        for student in students:
            self.emailer.send(template, student)

    def parse_args(args: list[str]) -> dict:
        parser = argparse.ArgumentParser(prog="Auto Reminder")
        parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.0.1")
        parser.add_argument("-c", "--config", type=argparse.FileType("r", encoding="UTF-8"), help="JSON encoded config file. Leave blank to use environment variables instead")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", "--api", action="store_true", help="Get students through the Moodle api")
        group.add_argument("-m", "--manual", type=argparse.FileType("r", encoding="UTF-8"), help="Get students from the specified grades file exported from Moodle")

        return vars(parser.parse_args(args))


def main():
    App().run()

if __name__ == "__main__":
    main()
