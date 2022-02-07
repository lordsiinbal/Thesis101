from mongoengine import *


class dc_user(Document):
    username = StringField()
    password = StringField()

    def to_json(self):
        return{
            "username": self.username,
            "password": self.password
        }
    