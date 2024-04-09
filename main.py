from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from model import Address, Student
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all origins (replace "*" with your actual frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# MongoDB connection setup
client = MongoClient("mongodb+srv://Aditya:Aditya%40123@cluster0.crqs9ng.mongodb.net/")
db = client["library_management"]
students_collection = db["students"]

# Define a root route to serve the student form template
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("student_form.html", "r") as file:
        html_content = file.read()
    return html_content


# Define API endpoints

from fastapi import Form

@app.post('/students')
async def create_student(name: str = Form(...), age: int = Form(...), city: str = Form(...), country: str = Form(...)):
    try:
        # Create Student model instance
        student = Student(name=name, age=age, address=Address(city=city, country=country))
        # Convert Pydantic model to dictionary
        student_dict = student.dict()
        # Insert student record into MongoDB
        result = students_collection.insert_one(student_dict)
        # Return success message
        return {"message": "Student created successfully"}
    except Exception as e:
        # Print the exception details
        print(e)
        # Return error message if an exception occurs
        return {"error": str(e)}


@app.get("/students", response_model=list[Student])
def list_students(country: str , age: int ):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(students_collection.find(query, {"_id": 0}))
    return students

@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: str):
    student = students_collection.find_one({"_id": ObjectId(student_id)}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{student_id}", status_code=204)
def update_student(student_id: str, student_data: Student):
    students_collection.update_one(
        {"_id": ObjectId(student_id)},
        {"$set": student_data.dict(exclude_unset=True)}
    )
    return {}

@app.delete("/students/{student_id}", status_code=200)
def delete_student(student_id: str):
    result = students_collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {}
