from fastapi import FastAPI
from app.config import Base, engine

# 🔁 Import explicite des modèles
from app.models import article, citation
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# 📦 Import des routes
from app.routes import article_routes, citation_routes, auth_routes, chat_routes 

# 🚀 Création de l'app FastAPI
app = FastAPI(
    title="DataTrace API",
    description="Analyse et gestion des citations de données dans les articles scientifiques",
    version="1.0.0"
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DataTrace API",
        version="1.0.0",
        description="Analyse et gestion des citations de données dans les articles scientifiques",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {}
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ou ["*"] pour tous
    allow_credentials=True,
    allow_methods=["*"],  # ou ["POST", "GET", "OPTIONS"]
    allow_headers=["*"],
)


# 🌐 Enregistrement des routes
app.include_router(chat_routes.router)

app.include_router(auth_routes.router)
app.include_router(article_routes.router)
app.include_router(citation_routes.router)

# 🧱 Création des tables au démarrage
@app.on_event("startup")
def on_startup():
    print("🔧 Initialisation des tables...")
    Base.metadata.create_all(bind=engine)
