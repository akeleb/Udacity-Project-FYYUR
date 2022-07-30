import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = False

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# For my local dataase I use the following commented line
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:yourdbpassword@localhost:5432/fyyurpdb'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://Akele:Aklexazsqldb14@pgforudacity.postgres.database.azure.com/fyyur?sslmode=require'
# This an online database I used on this project and this is just for dev/test purpose.
