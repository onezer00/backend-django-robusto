# Chat Access API

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen)](https://github.com/seu-usuario/seu-repo/actions)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://codecov.io/)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

---

## 📋 Descrição

API robusta em Django para gerenciamento de solicitações de acesso a um sistema de chat. Utiliza Celery para envio assíncrono de e-mails, RabbitMQ como broker e fornece uma interface administrativa customizada para análise e aprovação das solicitações.

---

## 🚀 Tecnologias

- Python 3.14+
- Django 4.x
- Django REST Framework
- Celery
- RabbitMQ
- PostgreSQL
- Docker & Docker Compose
- Pytest + Coverage
- Black + isort + pre-commit

---

## ⚙️ Setup do Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/chat-access-api.git
cd chat-access-api
```

### 2. Instalar dependências

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` baseado no `.env.example` com:

```env
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=*
ADMIN_BASE_URL=http://localhost:8000/admin
CHAT_BASE_URL=http://localhost:3000/chat
DEFAULT_FROM_EMAIL=seu@email.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua_senha
EMAIL_USE_TLS=True
```

---

## 🧪 Rodando os testes

```bash
pytest --cov=access
```

Para ver a cobertura completa:

```bash
coverage html
```

Abra `htmlcov/index.html` no navegador.

---

## 🧹 Lint & Formatação

Usamos [Black](https://black.readthedocs.io/) e [isort](https://pycqa.github.io/isort/):

```bash
black .
isort .
```

Ou use o pre-commit:

```bash
pre-commit install
pre-commit run --all-files
```

---

## 🐇 Celery (com RabbitMQ)

Execute o worker:

```bash
celery -A config worker -l info
```

Ou com Docker Compose (inclui o RabbitMQ):

```bash
docker-compose up -d
```

---

## 📁 Estrutura do Projeto

```text
.
├── access/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── tasks.py
│   ├── utils/
│   │   └── email_utils.py
│   └── tests/
│       └── test_chat_access_request.py
├── config/
│   ├── settings.py
│   ├── urls.py
├── manage.py
├── requirements.txt
├── requirements-test.txt
├── .env.example
└── README.md
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
