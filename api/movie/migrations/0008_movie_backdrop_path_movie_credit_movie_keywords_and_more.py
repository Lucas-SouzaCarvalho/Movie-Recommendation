# Generated by Django 5.0.4 on 2024-06-04 14:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movie', '0007_alter_movie_genres'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='backdrop_path',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='credit',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='keywords',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='original_language',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='production_companies',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='runtime',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='movie',
            name='tagline',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='genres',
            field=models.ManyToManyField(to='movie.genre'),
        ),
    ]
