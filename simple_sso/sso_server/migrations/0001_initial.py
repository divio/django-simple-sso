# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone
from django.conf import settings
import simple_sso.sso_server.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('private_key', models.CharField(default=simple_sso.sso_server.models.ConsumerSecretKeyGenerator(b'private_key'), unique=True, max_length=64)),
                ('public_key', models.CharField(default=simple_sso.sso_server.models.ConsumerSecretKeyGenerator(b'public_key'), unique=True, max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('request_token', models.CharField(default=simple_sso.sso_server.models.TokenSecretKeyGenerator(b'request_token'), unique=True, max_length=64)),
                ('access_token', models.CharField(default=simple_sso.sso_server.models.TokenSecretKeyGenerator(b'access_token'), unique=True, max_length=64)),
                ('timestamp', models.DateTimeField(default=timezone.now)),
                ('redirect_to', models.CharField(max_length=255)),
                ('consumer', models.ForeignKey(related_name='tokens', to='sso_server.Consumer')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
