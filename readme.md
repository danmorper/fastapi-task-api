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

#### JWT tokens
A JWT is composed of three parts:

1.	Header: Contains metadata about the token, including the type of token and the hashing algorithm used.
    ```json
    {
    "alg": "HS256",  # Algorithm used for the signature
    "typ": "JWT"     # Token type
    }
    ```
2.	Payload: Contains the claims. This is where the information, such as user details, is stored.
    ```json
    {
    "sub": "1234567890",  # Subject (usually the user ID)
    "name": "John Doe",   # Other user details (e.g., name)
    "iat": 1516239022     # Issued at time (Unix timestamp)
    }
    ```
3.	Signature: Used to verify the authenticity of the token and ensure that it has not been tampered with.

Tokens are generated with the following function.
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    """Given a data payload and an optional expiration delta, create an access token."""
    to_encode = data.copy()  # The payload (data) to encode into the JWT
    if expires_delta:
        expire = datetime.now(tz=timezone.utc) + expires_delta
    else:
        expire = datetime.now(tz=timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})  # Add expiration to the payload
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Create the JWT using the secret key and algorithm
```
Tokens have an expiration time, which is set when the token is generated. In this API, tokens expire after 30 minutes, as defined by the `ACCESS_TOKEN_EXPIRE_MINUTES` constant.

and verified with
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
```

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
- Error handling:
    The API ensures that meaningful and secure error messages are returned. Common errors include:
    - `401 Unauthorized`: When the user provides invalid or expired credentials (JWT token).
    - `404 Not Found`: When the requested resource (e.g., task or user) cannot be found.
### CRUD operations
CRUD (Create, Read, Update, Delete) operations in your FastAPI app for managing tasks, you’ll want to follow a systematic approach for each operation. Below is the implementation of each CRUD operation using FastAPI and SQLAlchemy.
#### 1. Create a new task
A POST endpoint creates a new task associated with the authenticated user (current_user), and stores it in the database. After committing the task, await db.refresh() loads the newly generated task’s ID from the database.
```python
from fastapi import status

@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate, 
    db: AsyncSession = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new task for the current authenticated user.
    """
    new_task = models.Task(
        title=task.title,
        description=task.description,
        is_complete=task.is_complete,
        owner_id=current_user.id
    )
    db.add(new_task)
    await db.commit()  # Save the task in the database
    await db.refresh(new_task)  # Refresh to get the new task with an ID
    return new_task
```

#### 2. Read: Retrieve All Tasks
A GET endpoint fetches tasks that belong to the currently authenticated user. It also includes pagination parameters (skip, limit) to avoid fetching too many tasks at once.
```python
@app.get("/tasks/", response_model=List[TaskCreate])
async def get_tasks(
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0, 
    limit: int = 10
):
    """
    Retrieve all tasks for the current authenticated user.
    Supports pagination with 'skip' and 'limit' parameters.
    """
    result = await db.execute(
        select(models.Task).filter(models.Task.owner_id == current_user.id).offset(skip).limit(limit)
    )
    tasks = result.scalars().all()  # Retrieve all tasks owned by the current user
    return tasks
```

#### 3. Read: Retrieve a single task by ID
A GET endpoint fetches a specific task by its task_id. If the task doesn’t exist or belongs to a different user, it raises a 404 Task not found error.
```python
@app.get("/tasks/{task_id}", response_model=TaskCreate)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Retrieve a specific task by its ID for the current authenticated user.
    """
    task = await db.get(models.Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

#### 4. Update an existing task
A PUT endpoint allows updating a task’s title, description, and completion status. If the task doesn’t belong to the current user or is not found, a 404 Task not found error is raised.
```python
@app.put("/tasks/{task_id}", response_model=TaskCreate)
async def update_task(
    task_id: int,
    task: TaskCreate,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing task by its ID for the current authenticated user.
    """
    db_task = await db.get(models.Task, task_id)
    if db_task is None or db_task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update the task fields
    db_task.title = task.title
    db_task.description = task.description
    db_task.is_complete = task.is_complete
    
    await db.commit()  # Commit the changes
    await db.refresh(db_task)  # Refresh to get the updated task from the database
    return db_task
```
#### 5. Delete a Task
A DELETE endpoint removes a task by its task_id if it belongs to the authenticated user. If the task isn’t found or belongs to another user, a 404 Task not found error is returned.
```python
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete a task by its ID for the current authenticated user.
    """
    task = await db.get(models.Task, task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await db.delete(task)
    await db.commit()
    return {"detail": "Task deleted"}
```

## Environment Variables
The project uses environment variables for configuration, such as the `SECRET_KEY` for JWT tokens. To set up the environment variables, create a `.env` file in the root of your project with the following contents:

```plaintext
SECRET_KEY=your-secure-secret-key
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_NAME=tasks_db
```
## Conclusion

This project showcases my ability to build a secure, high-performance API using FastAPI and PostgreSQL. The application is built with best practices in mind, including asynchronous programming, security, and scalability, making it suitable for production environments.

