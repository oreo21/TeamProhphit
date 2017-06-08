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
    super_admin = {}
    super_admin['name'] = "super_admin"
    super_admin['password'] = hashlib.sha512("password").hexdigest()
    db.admins.insert_one(super_admin)
    other_admins = {"name" : "other", "emails": [""]}
    db.admins.insert_one(other_admins)

def init_state():
    doc = {}
    doc["on"] = 0
    db.state.insert_one(doc)

if __name__ == "__main__":
    initialize()
