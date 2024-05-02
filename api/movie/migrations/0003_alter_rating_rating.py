# Generated by Django 5.0.4 on 2024-05-02 01:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0002_movie_poster_url_alter_rating_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='rating',
            field=models.FloatField(choices=[(0.5, '0.5 star'), (1.0, '1 star'), (1.5, '1.5 stars'), (2.0, '2 stars'), (2.5, '2.5 stars'), (3.0, '3 stars'), (3.5, '3.5 stars'), (4.0, '4 stars'), (4.5, '4.5 stars'), (5.0, '5 stars')], null=True),
        ),
    ]
