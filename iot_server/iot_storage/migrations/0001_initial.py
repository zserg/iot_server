# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-12 18:17
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Datanode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('node_path', models.TextField(default='')),
                ('data_type', models.CharField(default='str', max_length=8)),
                ('unit', models.CharField(default='', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Datapoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('created_at', models.IntegerField()),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot_storage.Datanode')),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('dev_id', models.CharField(max_length=16)),
                ('dev_type', models.CharField(default='', max_length=255)),
                ('description', models.TextField(default='')),
                ('attributes', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='datanode',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='iot_storage.Device'),
        ),
    ]