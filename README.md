# Photo Gallery

Galeria SPA com React/Vite, API FastAPI e PostgreSQL. Os uploads são validados pela proporção mínima de 0,5, convertidos para AVIF e mantidos abaixo de 1 MiB.

## Executar com Docker

```bash
docker compose up --build
```

Para usar o banco Aiven configurado localmente, copie `.env.sample` para `.env` e preencha `POSTGRES_PASSWORD`/`DATABASE_URL`. O arquivo `.env` não deve ser commitado.

Abra <http://localhost:5173>. A API fica disponível em <http://localhost:8000/docs>.

## Deploy no Render

O `Dockerfile` da raiz compila o React e serve a galeria e a API no mesmo serviço FastAPI. O banco continua na Aiven. A porta é lida de `PORT` (padrão: `10000`).

1. Envie estes arquivos para seu repositório GitHub.
2. No Render, crie um **Web Service** conectado ao repositório e à branch desejada.
3. Selecione **Docker**, deixe **Root Directory** vazio e use `./Dockerfile` como **Dockerfile Path**.
4. Em **Environment**, configure `DATABASE_URL` com a URL real da Aiven, usando `postgresql+psycopg://` e mantendo `?sslmode=require`. Exemplo: `postgresql+psycopg://avnadmin:SENHA@HOST:16238/defaultdb?sslmode=require`.
5. Configure o **Health Check Path** como `/health` e inicie o deploy. Deixe o comando Docker padrão.

Alternativamente, crie um **Blueprint** usando o `render.yaml` e preencha `DATABASE_URL` quando solicitado.

A galeria ficará em `https://SEU-SERVICO.onrender.com/` e a documentação em `/docs`. Não configure `VITE_API_URL` com localhost: o build usa caminhos relativos, então frontend e API compartilham a mesma origem e não precisam de CORS entre si. A senha fica apenas nas variáveis do Render; arquivos `.env` são excluídos do contexto Docker.

Para testar a imagem localmente, a partir da raiz:

```bash
docker build -t photo-gallery .
docker run --rm --env-file backend/.env -p 10000:10000 photo-gallery
```

Abra <http://localhost:10000>.

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
