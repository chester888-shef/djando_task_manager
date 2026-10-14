from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task 


class Command(BaseCommand):
    help = 'Шукає прострочені задачі і змінює їх статус на cancelled'

    def handle(self, *args, **options):
        now = timezone.now()
        
        overdue_tasks = Task.objects.filter(
            deadline__lt=now
        ).exclude(
            status__in=['done', 'cancelled']
        )
        
        count = overdue_tasks.count()

        if count > 0:
            overdue_tasks.update(status='cancelled')
            print(f'Успішно скасовано задач: {count}')
        else:
            print('Прострочених задач не знайдено')