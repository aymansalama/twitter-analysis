# Twitter Analysis
-------------------------

- After downloading Postgres, you should configure your settings.py, create a file called database_cred.py and include your database name, username and password.
```python
# Can be anything
db_name = 'twitter-analysis'
db_user = 'postgres'
db_password = '12345'
```

- After cloning the project run this command inside your virtual environment to install all the dependencies
`pip install -r /path/to/requirements.txt`

- After installing all the dependencies, you can proceed to migrate the database
`python manage.py migrate`

- If you are using any additional packages, remember to add them to the requirements file
`pip freeze > requirements.txt`


