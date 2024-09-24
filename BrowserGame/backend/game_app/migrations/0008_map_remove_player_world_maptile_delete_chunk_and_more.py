# Generated by Django 5.0.7 on 2024-08-27 00:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_app', '0007_player_pivot_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('width', models.IntegerField(default=250)),
                ('height', models.IntegerField(default=250)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='player',
            name='world',
        ),
        migrations.CreateModel(
            name='MapTile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('color', models.CharField(max_length=7)),
                ('layer', models.IntegerField()),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiles', to='game_app.map')),
            ],
            options={
                'unique_together': {('map', 'x', 'y', 'layer')},
            },
        ),
        migrations.DeleteModel(
            name='Chunk',
        ),
        migrations.DeleteModel(
            name='World',
        ),
    ]
