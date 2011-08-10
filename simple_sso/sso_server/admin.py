# -*- coding: utf-8 -*-
from django.contrib import admin
from simple_sso.sso_server.models import Client


admin.site.register(Client)
