# Twitter Analysis
-------------------------
Rule of Thumb to Structure Imports
-------------------------

```python
#Stdlib imports
from math import sqrt
from os.path import abspath

# Core Django imports
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Third-party app imports
from django_extensions.db.models import TimeStampedModel

# Imports from your apps
from splits.models import BananaSplit
```
- Easy the eyes to look for imports
- Source from Two Scopes of Django (Read it when you're free as it helps)

Steps To Set Up The Project
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


