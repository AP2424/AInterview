# Generated by Django 5.1.5 on 2025-05-19 09:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_interviewanswer_model_comment_interviewanswer_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicant',
            name='studyProgram',
        ),
    ]
