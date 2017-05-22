from pymongo import MongoClient
import hashlib, sqlite3

server = MongoClient()
# c = MongoClient('lisa.stuy.edu')
ourDB = server['ttpp'] 


# data[0] = username, data[1] = password, data[2] = action, data[3] = account_type
def authenticate(data):
    if data[2] == 'register':
        return register(data[0], data[1], data[3])
    else:
        return login(data[0], data[1], data[3])

def hashPass(password):
    return hashlib.sha512(password).hexdigest()

def userExists(username, account_type):
    if account_type == 'student':
        return bool(ourDB.students.find_one({"username": username}))
    elif account_type == 'admin':
        return bool(ourDB.admins.find_one({"username": username}))

def getPassword(username, account_type):
    if account_type == 'student':
        return ourDB.students.find_one({"username": username})['password']
    elif account_type == 'admin':
        return ourDB.admins.find_one({"username": username})['password']
    
# will fix later
def register(user, password, account_type):
    result = []
    if userExists(user, account_type):
        result = ['User already exists.', False]
    elif not user.isalnum() or not password.isalnum():
        result = ['Username and password may only consist of alphanumeric characters.', False]
    else:
        entry = {}
        entry['username'] = user
        entry['password'] = hashPass(password)
        ourDB.users.insert_one(entry)
        result =['Registration successful.', True]
    return result

def login(user, password, account_type):
    result = []
    if not userExists(user, account_type):
        result = ['User does not exist.', False]
        return result
    else:         
        p = getPassword(user, account_type)
        if (p != hashPass(password)):
            result = ['Incorrect password.', False]
        else:
            result = ['Login successful.', True]
    return result
