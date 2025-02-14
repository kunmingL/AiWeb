
import json


class Person:
    def __init__(self, name, age, email):
        self.name = name
        self.age = age
        self.email = email


def load_person_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return Person(data['name'], data['age'], data['email'])
