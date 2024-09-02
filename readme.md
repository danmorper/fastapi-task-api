# FastAPI Task Management API
## Overview
This project is a demonstration of a Task Management API built using FastAPI and PostgreSQL. The API allows users to register, authenticate, and manage their tasks with full CRUD (Create, Read, Update, Delete) operations. The application is designed with scalability and security in mind, leveraging asynchronous programming for performance optimization.

## Key features
- User Authentication: Secure user authentication using JWT (JSON Web Tokens).
- Task CRUD Operations: Users can create, read, update, and delete tasks that are associated with their account.
- Asynchronous Processing: The API uses asynchronous SQLAlchemy sessions for non-blocking I/O operations, making it suitable for high-performance applications.
- Security Best Practices: Passwords are hashed using bcrypt, and JWT tokens are used for secure session management.
- Scalable Architecture: The application is built with modularity in mind, allowing for easy expansion and maintenance.

## Tech Stack
- FastAPI: Web framework for building APIs in Python.
- PostgreSQL: Open-source relational database.
- SQLAlchemy: The Python SQL toolkit for SQL.
- Pydantic: Data validation.
- JWT (JSON Web Tokens): Securely transmitting information between parties as a JSON object.

## Project Structure
The project is structured to separate concerns and maintain clean, readable code. Below is a brief overview of the directory structure and key files:
```
├── app/
│   ├── main.py           # The main entry point of the application
│   ├── models.py         # SQLAlchemy models for User and Task
│   ├── schemas.py        # Pydantic models for request/response validation
│   ├── database.py       # Database connection setup and session management
│   ├── __init__.py       # Makes the app folder a Python package
├── tests/                # Unit tests for the API endpoints
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
├── alembic/              # Database migrations (if applicable)
```

## Implementation Details
### 1. User Registration and Authentication
Users can register by providing a unique username and password. The password is securely hashed using bcrypt before being stored in the database.
```python
@app.post("/register/")
async def register(user: UserCreate, db: AsyncSession = Depends(database.get_db)):
    db_user = await get_user(db, user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"msg": "User registered successfully"}
```
JWT tokens are generated for user authentication, ensuring that each request is securely validated.

### 2. Task Management
Authenticated users can manage their tasks with full CRUD functionality. Each task is associated with a user, ensuring data privacy and security.
- Create Task:
```python
@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: AsyncSession = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    new_task = models.Task(title=task.title, description=task.description, is_complete=task.is_complete, owner_id=current_user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task
```
- Retrieve Tasks: Users can fetch all tasks or specific tasks by ID.
### 3. Asynchronous Programming
The application leverages FastAPI’s support for asynchronous request handling, making use of async SQLAlchemy sessions to interact with PostgreSQL, ensuring the application can handle a large number of simultaneous requests efficiently.
```python
async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).filter(models.User.username == username))
    return result.scalars().first()
```

### 4. Security Considerations

- Password Hashing: Passwords are hashed using bcrypt, ensuring they are stored securely in the database.
- JWT Authentication: Secure JWT tokens are used for user authentication, allowing stateless communication between the client and server.
- Error Handling: Proper error handling is implemented to ensure that only meaningful and secure messages are returned to the client.

## Conclusion

This project showcases my ability to build a secure, high-performance API using FastAPI and PostgreSQL. The application is built with best practices in mind, including asynchronous programming, security, and scalability, making it suitable for production environments.