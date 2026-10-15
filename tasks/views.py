from django.shortcuts import render
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer, CommentSerializer, TaskStatusSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

ALLOWED_TRANSITIONS = {
    "backlog": ["in_progress", "cancelled"],
    "in_progress": ["review", "cancelled"],
    "review": ["done"],
    "done": [],
    "cancelled": [],
}



class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = ['status', 'priority', 'assignee', 'deadline']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['priority', 'deadline']

    def get_queryset(self):
        return Task.objects.select_related("assignee", "author")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        if instance.status in ['in_progress', 'review']:
            raise ValidationError(
                {"detail": "Не можна видаляти задачі в статусі In Progress або Review."}
            )
        instance.delete()

    @extend_schema(request=CommentSerializer, responses=CommentSerializer)
    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        task = self.get_object()

        if request.method == "GET":
            qs = task.comments.order_by("created_at")
            return Response(CommentSerializer(qs, many=True).data)

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)       


    @extend_schema(request=TaskStatusSerializer, responses=TaskSerializer)
    @action(detail=True, methods=["post"], url_path="status")
    def change_status(self, request, pk=None):
        task = self.get_object()

        serializer = TaskStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data["status"]

        if new_status not in ALLOWED_TRANSITIONS[task.status]:
            return Response(
                {"detail": f"Перехід {task.status} -> {new_status} заборонений"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if new_status == "done":
            if task.assignee is None:
                raise ValidationError(
                    {"status": "Не можна завершити задачу без виконавця."}
                )
            if task.deadline < timezone.now():
                raise ValidationError(
                    {"status": "Не можна завершити задачу: дедлайн минув."}
                )
        task.status = new_status
        task.save(update_fields=["status", "updated_at"])
        return Response(TaskSerializer(task).data)    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        now = timezone.now()
        
        overdue_tasks = self.get_queryset().filter(
            deadline__lt=now
        ).exclude(
            status__in=['done', 'cancelled']
        )
        page = self.paginate_queryset(overdue_tasks)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        now = timezone.now()
        stats_data = self.get_queryset().aggregate(
            total_tasks=Count('id'),
            done_tasks=Count('id', filter=Q(status='done')),
            active_tasks=Count('id', filter=~Q(status__in=['done', 'cancelled'])),
            overdue_tasks=Count('id', filter=Q(deadline__lt=now) & ~Q(status__in=['done', 'cancelled'])),
            high_priority=Count('id', filter=Q(priority='high'))
        )
        return Response(stats_data)