import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
#from sqladmin import Admin

#from db.session import get_engine
from api.dependencies import DEBUG
from api.routers import base

app = FastAPI(debug=DEBUG)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

if DEBUG:
    app.include_router(
        base.router_dev,
        prefix="/api-dev",
        tags=["開発環境"],
    )
else:
    app.include_router(
        base.router,
        prefix="/api",
        tags=["本番環境"],
    )

#if DEBUG:
    #dotenv_file = "db/.env"
    #admin_url = "/admin-dev"
#else:
    #dotenv_file = "db/.env.dev"
    #admin_url = "/admin"
#engine = get_engine(dotenv_file)
#admin = Admin(app, engine, base_url=admin_url)
#admin.add_view()

if DEBUG:
    from debug_toolbar.middleware import DebugToolbarMiddleware
    app.add_middleware(
        DebugToolbarMiddleware,
        #panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
    )
