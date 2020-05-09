# Twitter-Analysis
------------------------
## Description

This project allows user to collect tweets and analyze them using sentiment analysis methods. The user is able specify the keyword, starting and end dates, then the application will help collect tweets about that keyword between that time period. Once the tweets are analyzed, it will be displayed on the dashboard.

### Prerequisites

- You will need a Twitter developer account to be able to use this project.
    - Create a twitter_cred.py file inside your app directory, and include all your Twitter App credentials inside the file.

## Installation Guide
Installation of Python3 will be required to run the software. After cloning source code from GitHub, users may choose if they would like to keep
the libraries required in a Virtual Environment. 
### Installation and Set Up of Virtual Environment
Users can install virtual environment by running the following line in command prompt 
```
pip install virtualenv
```

After installation of virtualenv, users can create the virtualenv at the same level of directory as the root of the source code, by simply
running the following line in commpant prompt
```
virtualenv [Name Of Virtual Enviroment]
```

To activate the virtualenv users have to cd into the Scripts directory under the virtualenv folder.
An example of the path is as follow:
```
...\(Folder Name)\Test_ENV\Scripts>
```
When the Scripts folder is reached, simply run "activate" in the command line like so in the command line,
```
...\(Folder Name)\Test_ENV\Scripts>activate
```
Once the virtualenv is activated you will be able to see the name of your virtualenv at the left of your directory like so
```
(Test_ENV) ...\(Folder Name)\twitter-analysis>
```
After activating the virtualenv, you may cd into the project file with requirements.txt, which should be the like the directory above.

To begin, users will need to install all the libraries stated in the requirements.txt, like so
```
(Test_ENV) C:\Users\Kai Wey\Desktop\(Folder Name)\twitter-analysis>pip install -r requirements.txt
```
The download may took a short while.


### Database Setup
After succesful installations, users will need to setup their database depending on the database they will be using.
The full guide on database setup can be found here:
https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-DATABASES

After connecting the software to your database, you will need to migrate all existing models of the project to your database by running the 
following line in the project folder where "manage.py" is located. 
It should be found here:
```
(Test_ENV) ...\(Folder Name)\twitter-analysis\twitter_analysis>
```

Simply run the following line to make migrations file
```
py manage.py makemigrations
```
And to migrate into the database would be
```
py manage.py migrate
```

### Running the Server
After the database is setup, you may run the project in your localhost by running the following line:
```
py manage.py runserver
```

## API Guide
There are few endpoints that are available for users that do not want to use the GUI.

1. api/keyword/(GET)

Returns all keywords that have been searched before
```
{
"count": 17,
    "next": null,
    "previous": null,
    "results": [
        {
            "keyword": "harry maguire"
        },
        {
            "keyword": "tesla"
        },
        {
            "keyword": "pogba"
        },
        {
            "keyword": "lampard"
        },
        {
            "keyword": "justin bieber"
        }
}
```

2. api/tweet/(GET)

Returns all tweets in the database. There are few parameters that can be used to filter out the tweets.


    
|  Params |  Definition |
|---|---|
| keyword |Get tweets by the keyword entered |
| text | Get tweets that have the text |
| country  |  Get tweets by country |
|  polarity_gte |  Get tweets that have greater or equal polarity to the value entered |
|  polarity_lte  | Get tweets that have lesser or equal polarity to the value entered  |
| date_gte | Get tweets that are after specified date. eg. 2/1/2020 > 1/1/2020|
| date_lte | Get tweets that are before specified date eg. 1/1/2020 < 2/1/2020|
   

```
{
    "count": 1919,
    "next": "http://127.0.0.1:8000/api/tweet/?limit=100&offset=100",
    "previous": null,
    "results": [
        {
            "text": "RT @davidalorka: Harry Maguires Goal from the Man United end! COOMMMEEE OOONNN UUNNIIIIIITTEEEDDD!!  #MUFC #CHEMUN https://t.co/ABQIB",
            "keyword": "harry maguire",
            "polarity": "0.0000",
            "country": "Singapore",
            "stored_at": "2020-02-18T16:50:34.963990+08:00"
        },
        {
            "text": "RT @ManUtdChannel: Harry Maguires goal from the stands \n\nThat ball by Bruno Fernandes  https://t.co/t7tQ1KcQeH",
            "keyword": "harry maguire",
            "polarity": "0.0000",
            "country": "Dublin City, Ireland",
            "stored_at": "2020-02-18T16:50:35.586590+08:00"
        },
}
```
3. api/tweet/avg/(GET)

**Requires keyword in params**
Returns average polarity and top 10 words associated with the keyword.

```
{
    "Average Polarity": 0.12668988826815641,
    "Top 10 Words": [
        [
            "harry",
            96
        ],
        [
            "maguire",
            80
        ],
}
```

4. api/job/ (POST)

- Requires authentication, need to include user login credentials to use this endpoint
- Requires keyword, start_date, and end_date to create a job

    Creates a job to collect tweets based on the parameters.
```
{
    "keyword": "boxing",
    "start_date": "2020-02-23T14:37:37+08:00",
    "end_date": "2020-02-24T14:37:37+08:00",
}
```



