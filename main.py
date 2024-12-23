from fastapi import FastAPI
from routers.post import router

app = FastAPI()

app.include_router(router)


