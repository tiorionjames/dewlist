from fastapi import FastAPI
from server.routes import auth, users, tasks, managers, admin

app = FastAPI(title="Dewlist API")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(managers.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"message": "Welcome to Dewlist!"}
