# Items Management System (Distributed Kubernetes Solution)

Розподілене веб-рішення для управління елементами (CRUD REST API), що включає клієнтську частину (Frontend), серверну частину (Backend FastAPI), реляційну базу даних (PostgreSQL), окремий консольний застосунок міграцій (Migration Job) та Helm Chart для оркестрації в Kubernetes.

---

## 🏛️ Архітектура рішення

Система складається з таких компонентів:
1. **Frontend (SPA):** легкий клієнтський веб-інтерфейс на Nginx, що відображає список сутностей, дозволяє додавати нові записи, редагувати їх та видаляти через REST API.
2. **Backend API:** асинхронний REST-сервіс на **FastAPI** (Python 3.12) з ORM **SQLAlchemy** (Code-First підхід). Підтримує OpenAPI / Swagger UI за адресою `/docs`.
3. **Database (PostgreSQL):** реляційна СУБД, розгорнута в Kubernetes через `StatefulSet` із збереженням даних на постійному томі (`PersistentVolumeClaim`).
4. **Migration Job:** окремий консольний застосунок (`Dockerfile.migration`), що виконується в Kubernetes як `Job` (Helm post-install/post-upgrade hook) для автоматичного застосування міграцій до схеми бази даних перед стартом або оновленням сервісів.
5. **Ingress:** ресурс маршрутизації HTTP-трафіку, який спрямовує префікс `/api` до Backend API, а корінь `/` — до Frontend.
6. **Helm Chart (`k8s/webapp`):** пакет для комплексного розгортання та конфігурації всіх вищевказаних компонентів.

---

## 🛠️ Мова та технологічний стек

- **Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy, Pydantic
- **Frontend:** HTML5, CSS3, JavaScript (Fetch API), Nginx Alpine
- **Database:** PostgreSQL 16
- **CI/CD:** GitHub Actions (модульне тестування, збирання 3 Docker-образів, лінтинг та пакування Helm Chart)
- **Оркестрація:** Kubernetes, Helm v3/v4, Ingress NGINX

---

## 📦 Збирання та запуск Docker-образів локально

### 1. Збирання образів
```bash
# Backend API
docker build -t hut0r9n/lab1-api .

# Frontend
docker build -t hut0r9n/lab1-frontend -f frontend/Dockerfile .

# Migration Job
docker build -t hut0r9n/lab1-migration -f Dockerfile.migration .
```

### 2. Запуск локального середовища
```bash
# 1. Запуск бази даних PostgreSQL
docker run -d --name postgres-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgrespassword \
  -e POSTGRES_DB=itemsdb \
  -p 5432:5432 postgres:16-alpine

# 2. Застосування міграцій
docker run --rm \
  -e DATABASE_URL="postgresql://postgres:postgrespassword@host.docker.internal:5432/itemsdb" \
  hut0r9n/lab1-migration

# 3. Запуск Backend API
docker run -d --name api-service -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:postgrespassword@host.docker.internal:5432/itemsdb" \
  hut0r9n/lab1-api

# 4. Запуск Frontend
docker run -d --name frontend-service -p 80:80 \
  hut0r9n/lab1-frontend
```

Після запуску веб-інтерфейс доступний за адресою: `http://localhost`, а Swagger UI: `http://localhost:8000/docs`.

---

## 🧪 Запуск тестів

```bash
# Встановлення залежностей
pip install -r requirements.txt

# Запуск unit-тестів
pytest
```

---

## ☸️ Робота з Helm Chart (`k8s/webapp`)

Усі маніфести та конфігурації чарту розміщені в каталозі `k8s/webapp`.

### 1. Перевірка синтаксису (Linting)
```bash
helm lint k8s/webapp
```

### 2. Локальна генерація маніфестів (Dry-run / Template)
```bash
helm template lab k8s/webapp
```

### 3. Пакування чарту в архів
```bash
mkdir -p dist
helm package k8s/webapp --destination dist
```
Результатом буде архів, наприклад: `dist/webapp-0.1.0.tgz`.

### 4. Встановлення чарту в кластер Kubernetes
```bash
# Створення namespace та встановлення релізу 'lab'
helm upgrade --install lab k8s/webapp \
  -n webapp-lab \
  --create-namespace \
  --wait \
  --wait-for-jobs \
  --timeout 5m
```

### 5. Перевірка розгорнутих компонентів
```bash
kubectl -n webapp-lab get all
kubectl -n webapp-lab get pvc
kubectl -n webapp-lab get ingress
```

### 6. Видалення релізу
```bash
helm uninstall lab -n webapp-lab
```
