# Generated by Django 5.1.5 on 2025-02-10 16:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_question_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewmodel',
            name='questionsList',
        ),
        migrations.AddField(
            model_name='question',
            name='model',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main.interviewmodel'),
        ),
    ]
