from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Task
from datetime import timedelta

User = get_user_model()

class TaskOverdueTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.client.force_authenticate(user=self.user)
        
        now = timezone.now()
        
        Task.objects.create(
            name="Old Task", status="backlog", priority="medium", 
            deadline=now - timedelta(days=1), author=self.user
        )
        Task.objects.create(
            name="Future Task", status="backlog", priority="medium",
            deadline=now + timedelta(days=1), author=self.user
        )
        Task.objects.create(
            name="Done Task", status="done", priority="medium",
            deadline=now - timedelta(days=1), author=self.user
        )

    def test_overdue_endpoint_returns_only_active_overdue_tasks(self):
        response = self.client.get('/api/tasks/overdue/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('results', response.data)
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Old Task")

class TaskStatsTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='statsuser', password='password123')
        self.client.force_authenticate(user=self.user)
        now = timezone.now()
        

        Task.objects.create(name="T1", status="done", priority="low", deadline=now + timedelta(days=1), author=self.user)

        Task.objects.create(name="T2", status="in_progress", priority="high", deadline=now + timedelta(days=1), author=self.user)

        Task.objects.create(name="T3", status="backlog", priority="medium", deadline=now - timedelta(days=1), author=self.user)

    def test_stats_endpoint_returns_correct_counts(self):

        response = self.client.get('/api/tasks/stats/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        self.assertEqual(data['total_tasks'], 3)
        self.assertEqual(data['done_tasks'], 1)
        self.assertEqual(data['active_tasks'], 2)  
        self.assertEqual(data['overdue_tasks'], 1) 
        self.assertEqual(data['high_priority'], 1) 

class TaskLimitTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='limituser', password='password123')
        self.client.force_authenticate(user=self.user)

    def test_cannot_create_more_than_10_tasks(self):
        for i in range(10):
            Task.objects.create(
                name=f"Task {i}", 
                status="backlog", 
                priority="medium", 
                deadline=timezone.now() + timedelta(days=1),
                author=self.user
            )
        payload = {
            "name": "Task 11 - The Forbidden One",
            "status": "backlog",
            "priority": "medium",
            "deadline": (timezone.now() + timedelta(days=1)).isoformat()
        }
        response = self.client.post('/api/tasks/', data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)       