# Generated by Django 2.2.7 on 2020-02-08 08:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('analyze_tweets', '0004_auto_20200208_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='modified',
            new_name='last_modified',
        ),
        migrations.RenameField(
            model_name='job',
            old_name='user_id',
            new_name='user',
        ),
    ]
