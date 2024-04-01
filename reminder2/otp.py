import random

otp_store = {}


def generate_otp():
    return str(random.randint(100000, 999999))


def store_otp(email, otp):
    otp_store[email] = otp


def get_otp(email):
    return otp_store.get(email)


def clear_otp(email):
    if email in otp_store:
        del otp_store[email]
