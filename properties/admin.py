# properties/admin.py

from django.contrib import admin
from .models import Agent, Property

admin.site.register(Agent)
admin.site.register(Property)
