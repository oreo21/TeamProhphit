from pymongo import MongoClient
import hashlib, sqlite3

server = MongoClient()
# c = MongoClient('lisa.stuy.edu')
ourDB = server['database'] 

def authenticate(data):
    if data[2] == 'Register':
        return register(data[0], data[1])
    else:
        return login(data[0], data[1])

def hashPass(password):
    return hashlib.sha512(password).hexdigest()

def userExists(username):
    #return bool(ourDB.users.find_one({"username": username}))
    cursor = ourDB.users.find()
    for user in cursor:
        if username == user['username']:
            return True
    return False

def register(user, password):
    result = []
    if (userExists(user)):
        result = ['User already exists.', False]
    elif not user.isalnum() or not password.isalnum():
        result = ['Username and password may only consist of alphanumeric characters.', False]
    else:
        entry = {}
        entry['username'] = user
        entry['password'] = hashPass(password)
        ourDB.users.insert_one(entry)
        result =['Registration successful.', False]
    return result

def login(user, password):
    result = []
    if not userExists(user):
        result = ['User does not exist.', False]
    else:
        p = ourDB.users.find_one({"username": user})['password']
        if (p != hashPass(password)):
            result = ['Incorrect password.', False]
        else:
            result = ['Login successful.', True]
    return result


def userExistsSQL(username, c):
    s = c.execute("SELECT name FROM users")
    for r in s:
        name = r[0]
        if username == name:
            return True
    return False

def registerSQL(user, password):
    result = []
    bd = sqlite3.connect('data/bd.db')
    c = bd.cursor()
    if (userExistsSQL(user, c)):
        result = ['User already exists.', False]
    elif not user.isalnum() or not password.isalnum():
        result = ['Username and password may only consist of alphanumeric characters.', False]
    else:
        p = hashPass(password)
        c.execute("INSERT INTO users VALUES ('%s', '%s')"%(user, p))
        bd.commit()
        bd.close()
        result = ['Registration successful.', False]
    return result

def loginSQL(user, password):
    result = []
    bd = sqlite3.connect('data/bd.db')
    c = bd.cursor()
    if (userExistsSQL(user, c) == False):
        result = ['User does not exist.', False]
    else:
        s = c.execute("SELECT password FROM users WHERE name = '%s'"%(user))
        p = s.fetchone()[0]
        if (p != hashPass(password)):
            result = ['Incorrect password.', False]
        else:
            result = ['Login successful.', True]
    return result
