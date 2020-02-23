# Generated by Django 2.2.7 on 2020-02-18 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze_tweets', '0008_merge_20200217_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='avg_polarity',
            field=models.DecimalField(decimal_places=5, max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='keyword',
            name='tweet_count',
            field=models.BigIntegerField(null=True),
        ),
    ]
