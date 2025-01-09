from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException, Body
from pydantic import BaseModel, Field
from starlette import status


app = FastAPI()

BOOKS = [
    {'id': 1, 'author': 'devbaoo', 'category': 'comic', 'published_date': 2012},
    {'id': 2, 'author': 'Hung', 'category': 'science', 'published_date': 2012},
    {'id': 3, 'author': 'Duc', 'category': 'comic', 'published_date': 2020},
    {'id': 4, 'author': 'Khang', 'category': 'math', 'published_date': 2014},
    {'id': 5, 'author': 'Truong', 'category': 'kocogi', 'published_date': 2000},
    {'id': 6, 'author': 'Teo', 'category': 'history', 'published_date': 2012},
]

class Book:
    id = int
    author = str
    category = str
    published_date: int


    def __init__(self, id, author, category, published_date):
        self.id = id
        self.author = author
        self.category = category
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on create", default=None)
    author: str = Field(min_length=1)
    category: str = Field(min_length=1)
    published_date: int = Field(gt=1900)
    model_config = {
        "json_schema_extra": {
            "example": {
                "author": "devbaoo",
                'category': 'comic',
                'published_date': 2029
            }
        }
    }


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books():
    return (BOOKS )

@app.get("/books/{id}", status_code = status.HTTP_200_OK)
async def get_book(id: int = Path(gt=0)):
    for book in BOOKS:
        if book['id'] == id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_category(category: str):
    books_to_return = []
    for book in BOOKS:
        if book['category'].casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(new_book: BookRequest):
    if any(book['id'] == new_book.id for book in BOOKS if new_book.id is not None):
        raise HTTPException(status_code=400, detail="Book ID already exists.")

    book_id = new_book.id if new_book.id is not None else len(BOOKS) + 1
    book = {"id": book_id, "author": new_book.author, "category": new_book.category, "published_date": new_book.published_date}
    BOOKS.append(book)
    return {"message": "New book created successfully", "book": book}


@app.put("/books/{id}", status_code=status.HTTP_200_OK)
async def update_book(id: int, update_book: BookRequest):
    for book in BOOKS:
        if book['id'] == id:
            book["author"] = update_book.author
            book["category"] = update_book.category
            book["published_date"] = update_book.published_date
            return {"message": "Book updated successfully", "book": book}

    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{id}", status_code=status.HTTP_200_OK, response_description="Book deleted successfully")
async def delete_book(id: int = Path(gt=0)):
    for book in BOOKS:
        if book['id'] == id:
            BOOKS.remove(book)
        else: raise HTTPException(status_code=404, detail="Book not found")




@app.get("/books/filter-by-published_date/")
async def filter_books_by_published_date(published_date: int):
    filtered_books = [book for book in BOOKS if book['published_date'] == published_date]
    return filtered_books
