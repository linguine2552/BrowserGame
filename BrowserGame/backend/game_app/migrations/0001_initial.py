# Generated by Django 5.0.7 on 2024-08-18 19:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='World',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('seed', models.IntegerField()),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_id', models.CharField(max_length=100, unique=True)),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_app.world')),
            ],
        ),
        migrations.CreateModel(
            name='Chunk',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('x', models.IntegerField()),
                ('y', models.IntegerField()),
                ('terrain_data', models.JSONField()),
                ('biome_data', models.JSONField()),
                ('environment_data', models.JSONField()),
                ('world', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game_app.world')),
            ],
        ),
    ]
