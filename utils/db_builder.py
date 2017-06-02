from pymongo import MongoClient
from db_manager import *
import csv
import hashlib


server = MongoClient()
#server = MongoClient("lisa.stuy.edu")
db = server['ttpp']

def initialize():
    init_admin()
    init_state()

def init_admin():
    admin = {}
    admin['username'] = "admin"
    admin['password'] = hashlib.sha512("password").hexdigest()
    db.admins.insert_one(admin)

def init_state():
    doc = {}
    doc["on"] = 0
    db.state.insert_one(doc)

if __name__ == "__main__"
initialize()
