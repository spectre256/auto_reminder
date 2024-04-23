import argparse
import json
from string import Template

class App:
    config: dict
    student_finder: StudentFinder
    emailer: Emailer

    def __init__(self, config_file: str):
        self.config = json.load(config_file)
        self.config["threshold"] = timedelta(days=self.config["threshold"])
        self.student_finder = ApiFinder(self.config)
        self.emailer = Emailer(self.config)

    def run(self):
        students = self.student_finder.get_missing()
        print(students)
        template = Template(self.config["template"])
        for student in students:
            self.emailer.send(template, student)

    # def parse_args(self) -> argparse.NameSpace:
    #     parser = argparse.ArgumentParser()
    #     parser.add_argument()

def main():
    App("config.json").run()

if __name__ == "__main__":
    main()
