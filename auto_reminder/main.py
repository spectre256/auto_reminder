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

from auto_reminder.models import StudentFinder
from auto_reminder.api_finder import ApiFinder
from auto_reminder.manual_finder import ManualFinder
from auto_reminder.emailer import Emailer
import argparse
import json
import sys
import os
from string import Template
import asyncio
import logging
import logging.config


logger = logging.getLogger("auto_reminder")
with open("logging.json") as log_config:
    logging.config.dictConfig(json.load(log_config))


class App:
    config: dict
    student_finder: StudentFinder

    def __init__(self):
        args = App.parse_args(sys.argv[1:]) # The [1:] skips the first argument which is the filename
        logger.info("Parsed args")
        self.config = json.load(args["config"]) if args["config"] else os.environ
        logger.info("Loaded config")
        self.student_finder = (ApiFinder(self.config) if args["api"]
                               else ManualFinder(self.config, args["manual"]))


    async def run(self):
        students = list(self.student_finder.get_missing())
        logger.info("Found students with missing assignments")
        logger.debug("Students with missing assignments: %s", students)
        template = Template(self.config["template"])

        async with Emailer(self.config) as emailer, asyncio.TaskGroup() as tg:
            for student in students:
                tg.create_task(emailer.send(template, student))
                logger.debug(f"Created email task for student '{student.name}'")


    def parse_args(args: list[str]) -> dict:
        parser = argparse.ArgumentParser(prog="Auto Reminder")
        parser.add_argument("-v", "--version", action="version", version="%(prog)s 0.0.1")
        parser.add_argument("-c", "--config", type=argparse.FileType("r", encoding="UTF-8"), help="JSON encoded config file. Leave blank to use environment variables instead")

        group = parser.add_mutually_exclusive_group()
        group.add_argument("-a", "--api", action="store_true", help="Get students through the Moodle api")
        group.add_argument("-m", "--manual", type=argparse.FileType("r", encoding="UTF-8"), help="Get students from the specified grades CSV file exported from Moodle")

        return vars(parser.parse_args(args))


def main():
    asyncio.run(App().run())

if __name__ == "__main__":
    main()
