#!flask/bin/python
import os
import unittest
from datetime import datetime, timedelta

from config import basedir
from app import app, db
from app.models import User, Post


class TestCase(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
