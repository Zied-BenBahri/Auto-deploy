from fastapi import FastAPI

app = FastAPI(
    title="My FastAPI Project",
    description="API for my project",
    version="0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI project!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
