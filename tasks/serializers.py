from rest_framework import serializers
from .models import Task
from .models import Task, Comment
from django.utils import timezone


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id", "name", "description", "status", "priority",
            "assignee", "author", "deadline", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "author","status", "created_at", "updated_at"]

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Дедлайн не може бути в минулому.")
        return value  


    def validate_assignee(self, value):
        if value is None:
            return value
        active_statuses = ["backlog", "in_progress", "review"]
        query = Task.objects.filter(assignee=value, status__in=active_statuses)
        if self.instance:
            query = query.exclude(id=self.instance.id)
        if query.count() >= 10:
            raise serializers.ValidationError("Цей виконавець вже має максимум активних задач (10).")
            
        return value


    def validate(self, attrs):
        if self.instance:
            if self.instance.status in ['done', 'cancelled']:
                raise serializers.ValidationError("Задачі зі статусом Done або Cancelled не можна редагувати.")

            if self.instance.status in ['review', 'done']:
                if 'assignee' in attrs and attrs['assignee'] != self.instance.assignee:
                    raise serializers.ValidationError(
                        {"assignee": "Не можна міняти виконавця на стадії Review або Done."}
                    )
                    
        return attrs

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "task", "author", "text", "created_at"]
        read_only_fields = ["id", "task", "author", "created_at"]


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Task._meta.get_field("status").choices)