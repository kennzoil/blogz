def valid_username(username):
    """checks validity of given username"""
    valid = True
    if len(username) < 3 or len(username) > 20:
        valid = False
    elif " " in username:
        valid = False
    return valid

def valid_password(password):
    """checks validity of given password"""
    valid = True
    if password == "":
        valid = False
    elif len(password) < 3 or len(password) > 20:
        valid = False
    elif " " in password:
        valid = False
    return valid

def passwords_match(password, passconfirm):
    """compares password and password confirmation to check for equality"""
    valid = True
    if password != passconfirm:
        valid = False
    return valid