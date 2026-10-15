Markdown

# Task Management API (Mini-Jira)

REST API для управління задачами, розроблене як плавний перехід від FastAPI до екосистеми Django. Проєкт базується на Django REST Framework (DRF) з використанням PostgreSQL та Docker.

## 🚀 Стек технологій
- **Backend:** Django 6.1, Django REST Framework
- **База даних:** PostgreSQL
- **Аутентифікація:** SimpleJWT (JSON Web Tokens)
- **Інфраструктура:** Docker, Docker Compose
- **Документація API:** drf-spectacular (Swagger UI)

## ⚙️ Основний функціонал
- **JWT-Авторизація:** Захищені ендпоінти з перевіркою токенів.
- **Складна бізнес-логіка:** 
  - Обмеження створення не більше 10 задач на одного користувача.
  - Жорстка перевірка логіки переходів статусів (наприклад, з `Done` не можна повернути в `Backlog`).
  - Заборона видалення задач зі статусами `In Progress` або `Review`.
- **Кастомні ендпоінти:**
  - `/api/tasks/stats/` — агрегація статистики по базі даних (активні, виконані, прострочені).
  - `/api/tasks/overdue/` — список задач, у яких вийшов дедлайн.
- **Розширена вибірка:** Пагінація, сортування, пошук та точні фільтри через `django-filter`.
- **Фонові задачі:** Кастомна management-команда `mark_overdue` для масового оновлення статусів прострочених задач (підготовлено для cron).

## 🛠 Як запустити локально

1. Склонуйте репозиторій:
   ```bash
   git clone [https://github.com/chester888-shef/djando_task_manager.git](https://github.com/chester888-shef/djando_task_manager.git)
   cd djando_task_manager

    Створіть файл .env у корені проєкту (додайте свої значення):
    Фрагмент коду

    DB_NAME=postgres
    DB_USER=postgres
    DB_PASSWORD=your_password
    DB_HOST=db
    DB_PORT=5432

    Запустіть контейнери:
    Bash

    docker compose up -d --build

    Застосуйте міграції бази даних:
    Bash

    docker compose exec web python manage.py migrate

📚 Документація

Після успішного запуску документація Swagger UI доступна за адресою:
http://localhost:8000/api/schema/swagger-ui/
🧪 Тестування

Проєкт покритий юніт-тестами (перевірка лімітів, фільтрації та кастомних action). Для запуску тестів виконайте:
Bash

docker compose exec web python manage.py test tasks


