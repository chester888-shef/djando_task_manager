from django.contrib import admin
from .models import User, Task, Comment
from django.contrib.auth.admin import UserAdmin

admin.site.register(User, UserAdmin)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'priority', 'deadline' )
    search_fields = ('name',)
    list_filter = ('status', 'priority')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author', 'created_at')
    list_filter = ('author',)
    






