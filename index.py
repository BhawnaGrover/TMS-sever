from fastapi import FastAPI
from apis.user_router import user_router_tms
from apis.task_router import task_router_tms
app = FastAPI()

def include_router(app):
    app.include_router(user_router_tms)
    app.include_router(task_router_tms)

def start_application():
    include_router(app)
    return app

app = start_application()
