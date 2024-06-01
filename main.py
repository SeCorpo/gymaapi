import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import AsyncSessionLocal, engine, Base
from router import userRouter, gymaRouter, authRouter, mineRouter, pubRouter, personRouter
from _test import testRouter


logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def test_database_connection():
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text('SELECT 1'))
            await session.commit()
            logging.info("Successfully connected to the database.")
        except SQLAlchemyError as e:
            logging.error(f"Failed to connect to the database: {e}")


@app.on_event("startup")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(authRouter.router)
app.include_router(userRouter.router)
app.include_router(gymaRouter.router)
app.include_router(mineRouter.router)
app.include_router(pubRouter.router)
app.include_router(testRouter.router)
app.include_router(personRouter.router)

app.mount("/images/large", StaticFiles(directory="images/large"), name="large_images")
app.mount("/images/medium", StaticFiles(directory="images/medium"), name="medium_images")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
