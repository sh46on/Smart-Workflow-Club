from django.contrib import admin

# Register your models here.
from django.contrib import admin
from events.models import *

admin.site.register(User)
admin.site.register(Club)
admin.site.register(Event)
admin.site.register(Feedback)
