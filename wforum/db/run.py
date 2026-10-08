from fastapi import FastAPI

from .api import auth, comments, notification, posts, topics, users, votes

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(topics.router)
app.include_router(comments.router)
app.include_router(votes.router)
app.include_router(notification.router)
