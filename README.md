# Twitter-Analysis
------------------------
## Description

This project allows user to collect tweets and analyze them using sentiment analysis methods. The user is able specify the keyword, starting and end dates, then the application will help collect tweets about that keyword between that time period. Once the tweets are analyzed, it will be displayed on the dashboard.

### Prerequisites

- You will need a Twitter developer account to be able to use this project.
    - Create a twitter_cred.py file inside your app directory, and include all your Twitter App credentials inside the file.


### API
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



