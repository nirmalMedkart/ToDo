from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin): 
    list_display = ['id','user','title', 'desc','start_date','end_date','started','ended']

