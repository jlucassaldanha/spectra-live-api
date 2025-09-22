# 🎥 Spectra Live API
![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-000?logo=Railway)
![Python](https://shields.io/badge/Python-gray?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-gray?logo=fastapi)
![PostgresSQL](https://img.shields.io/badge/PostgreSQL-gray?logo=postgresql)

## 📌 Sobre o projeto
O **Spectra Live API** é a RestAPI para o **[Spectra Live](https://spectralive.vercel.app)**.

**👉 Acesse a API em produção por aqui: [Spectra Live API](https://spectralive-api.up.railway.app/redoc)**
**👉 Acesse o site em produção por aqui: [Spectra Live](https://spectralive.vercel.app)**

## 🛠 Tecnologias Utilizadas
- **API** → Python, FastAPI
- **DB** → PostgreSQL, SQLAlchemy  
- **Deploy e CI/CD simplificados** → Railway

## 🎯 Funcionalidades
- Login e Logout → Autenticação via conta da Twitch e JWT próprio
- Requests com API da Twitch
- Comunicação com banco de dados PostgresSQL

## 🔧 Como rodar localmente
### Backend
Para rodar com API local
``` bash
# Clonar o repositório
git clone https://github.com/jlucassaldanha/spectra-live-api.git

# Acessar pasta
cd spectra-live-api

# Instalar dependências
pip install -r requirements.txt

# Rodar projeto
uvicorn app.main:app --reload
```
Necessário um .env com as variaveis:
``` shell
CLIENT_ID = 
CLIENT_SECRET = 
ALGORITHM = 
SECRET_KEY = 
DATABASE_URL =
API_URL = 
FRONTEND_URL = 
```

A API tem o objetivo de servir a aplicação Spectra Live, portando recomendo a utilização do Frontend também.
### Frontend

```bash
# Clonar o repositório
git clone https://github.com/jlucassaldanha/spectra-live.git

# Acessar pasta
cd spectra-live

# Instalar dependências
npm install

# Rodar projeto
npm run dev
```
#### Para rodar localmente com aplicativo próprio da twitch
- Acesse o [console da Twitch](https://dev.twitch.tv/console/apps) e faça login
- Registre seu aplicativo 
- Configure as URLs de redirecionamento OAuth para a sua URL seguindo o modelo: **https://sua_url/viewers**
- Categoria: **Analytics Tool**
- Tipo de cliente: **Confidencial**
- Salve o aplicativo
- Copie seu **ID do cliente**
- Copie seu **Segredos**

## 📂 Repositórios
- **Backend**: [github.com/jlucassaldanha/spectra-live-api](github.com/jlucassaldanha/spectra-live-api)
- **Frontend**: [github.com/jlucassaldanha/spectra-live](github.com/jlucassaldanha/spectra-live)

## 📜 Licença
Este projeto está licenciado sob a **MIT License** – veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

>ℹ️ Nota sobre futuras versões
O autor reserva o direito de relicenciar versões futuras deste projeto sob a GPLv3, garantindo que ele continue sempre open source.
Versões já publicadas sob a MIT continuarão disponíveis e válidas sob os termos da MIT.

## 📫 Contato
[LinkedIn: João Lucas Saldanha](https://www.linkedin.com/in/joao-lucas-saldanha/)