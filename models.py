from mongoengine import Document, StringField

class Usuarios(Document):
    username = StringField()
    password = StringField()