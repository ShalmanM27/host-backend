from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import feed, comment, learning, dao, moderation, streak, profile

app = FastAPI(title="Web3 Productivity Social App")

# CORS - allow frontend (adjust origins as needed)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(feed.router)
app.include_router(comment.router)
app.include_router(learning.router)
app.include_router(dao.router)
app.include_router(moderation.router)
app.include_router(streak.router)
app.include_router(profile.router)

# Root
@app.get("/")
async def root():
    return {"message": "Web3 Productivity Social App Backend Running"}
