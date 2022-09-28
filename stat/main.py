from fastapi import FastAPI, status, HTTPException
from models import Page
import services


app = FastAPI()

@app.post("/create_page", response_model=Page)
async def new_page(page: Page):
    data, stat = services.create_new_page(page)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/update_page")
async def update_page(page_name: str, user_id: str, page_id: str):
    data, stat = services.update_page(page_name, user_id, page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.delete("/delete_page")
async def delete_page(user_id: str, page_id: str):
    data, stat = services.delete_page(user_id, page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.get("/pages", response_model=list[Page])
async def get_pages(user_id: str):
    data, stat = services.get_pages(user_id)
    return data

@app.put("/pages/{page_id}/new_like/", response_model=Page)
async def new_like(page_id: str):
    data, stat = services.new_like(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/pages/{page_id}/new_follower/", response_model=Page)
async def new_follower(page_id: str):
    data, stat = services.new_follower(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/pages/{page_id}/new_follow_request/", response_model=Page)
async def new_follow_request(page_id: str):
    data, stat = services.new_follow_request(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/pages/{page_id}/undo_like/", response_model=Page)
async def undo_like(page_id: str):
    data, stat = services.undo_like(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/pages/{page_id}/undo_follower/", response_model=Page)
async def undo_follower(page_id: str):
    data, stat = services.undo_follower(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data

@app.put("/pages/{page_id}/undo_follow_request/", response_model=Page)
async def undo_follow_request(page_id: str):
    data, stat = services.undo_follow_request(page_id)
    if stat != status.HTTP_200_OK:
        raise HTTPException(status_code=stat, detail=data)
    return data