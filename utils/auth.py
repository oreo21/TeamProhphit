import hashlib, sqlite3

def authenticate(data):
    if data[2] == 'Register':
        return register(data[0], data[1])
    else:
        return login(data[0], data[1])

def hashPass(password):
    return hashlib.sha512(password).hexdigest()

def userExists(username, c):
    s = c.execute("SELECT name FROM users")
    for r in s:
        name = r[0]
        if username == name:
            return True
    return False

def register(user, password):
    result = []
    bd = sqlite3.connect('data/bd.db')
    c = bd.cursor()
    if (userExists(user, c)):
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

def login(user, password):
    result = []
    bd = sqlite3.connect('data/bd.db')
    c = bd.cursor()
    if (userExists(user, c) == False):
        result = ['User does not exist.', False]
    else:
        s = c.execute("SELECT password FROM users WHERE name = '%s'"%(user))
        p = s.fetchone()[0]
        if (p != hashPass(password)):
            result = ['Incorrect password.', False]
        else:
            result = ['Login successful.', True]
    return result
