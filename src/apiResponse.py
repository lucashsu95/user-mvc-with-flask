from flask_responses import json_response

def success(data, status_code):
    return json_response({"success":True,"data":data }, status_code=status_code)

def fail(message, status_code):
    return json_response({"success":False,"message":message}, status_code=status_code)

def email_exists():
    return fail("MSG_EMAIL_EXISTS", 400)

def user_not_exists():
    return fail("MSG_USER_NOT_EXISTS", 404)

def missing_fields():
    return fail("MSG_MISSING_FIELDS", 400)

def password_too_short():
    return fail("MSG_PASSWORD_TOO_SHORT", 400)

def invalid_login():
    return fail("MSG_INVALID_LOGIN", 401)

def invalid_access_token():
    return fail("MSG_INVALID_ACCESS_TOKEN",401)

def permission_deny():
    return fail("MSG_PERMISSION_DENY", 403)
