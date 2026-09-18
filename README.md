# Photo Gallery

Galeria SPA com React/Vite, API FastAPI e PostgreSQL. Os uploads são validados pela proporção mínima de 0,5, convertidos para AVIF e mantidos abaixo de 1 MiB.

## Executar com Docker

```bash
docker compose up --build
```

Abra <http://localhost:5173>. A API fica disponível em <http://localhost:8000/docs>.

## Desenvolvimento local

Backend:

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

