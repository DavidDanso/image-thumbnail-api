from fastapi import FastAPI
from . import models
from .database import engine
from .routers import auth, users, uploads
from fastapi.middleware.cors import CORSMiddleware

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

###################### GET ROUTERS FOR API #####################
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(uploads.router)


@app.get("/")
def read_root():
    return {"response": "Image Thumbnail API"}