# Coding Style Guide for Python Discord Bot with MongoDB

## 1. Code Structure and Organization

### 1.1 Folder Structure

Maintain a clear, modular folder layout:

```plaintext
capy/
├── src/
│   ├── capy_backend/  
│   │   ├── db/                    # Database models and connection utilities
│   │   ├── mods/                  # Additional modules for extended functionalities
│   │   ├── res/                   # Static resources like images, JSON files, etc.
│   │   ├── utils/                 # Utility/helper functions
│   ├── capy_discord/  
│   │   ├── cogs/                  # Separate modules for bot commands/features
│   │   ├── bot.py
│   ├── config.py                  # Configuration constants
│   └── main.py                    # Entry point of the bot
├── tests/                         # Unit and integration tests
│   ├── capy_backend/  
│   │   ├── db/                    # Database models and connection utilities
│   │   ├── mods/                  # Additional modules for extended functionalities
│   │   ├── res/                   # Static resources like images, JSON files, etc.
│   │   ├── utils/                 # Utility/helper functions
│   ├── capy_discord/  
│   │   ├── cogs/                  # Separate modules for bot commands/features
│   │   ├── bot.py
├── .env                           # Environment variables and secrets
├── requirements.txt               # Python dependencies
├── requirements_dev.txt           # Development dependencies
├── style.md                       # Coding style guide
├── test.md                        # Testing script
└── updater.py                     # Script for updating host
```

### 1.2 Code Structure

- Use a class-based design for modularity:
  - Define a `Cog` for each bot feature (e.g., moderation, profiles).
  - Separate utility methods by category into individual files for clarity.

---

## 2. Python Conventions

### 2.1 Variables and Functions

- Use **snake_case** for variables and functions:

```python
def get_user_profile(user_id: str) -> dict:
    ...
```

### 2.2 Classes

- Use **PascalCase** for class names:

```python
class UserProfile:
    ...
```

### 2.3 Files

- Use **lowercase_with_underscores** for file names (e.g., `user_profiles.py`).

---

## 3. Comments and Documentation

### 3.1 Inline Comments

- Provide concise, meaningful inline comments above complex code:

```python
# Fetch the user profile from the database
user_profile = db.get_user(user_id)
```

### 3.2 Function and Class Docstrings

- Write docstrings for all public functions, methods, and classes. Follow the Google style for docstrings:

```python
def fetch_user_data(user_id: str) -> dict:
    """
    Fetch user data from the database.

    Args:
        user_id (str): The unique ID of the user.

    Returns:
        dict: The user profile data.
    """
```

### 3.3 Module Docstrings

- Include a brief description at the top of each file:

```python
"""
This module handles MongoDB connection and operations
for user profiles.
"""
```

---

## 4. Semantic Guidelines

### 4.1 Code Readability

- Prioritize clarity over brevity:

```python
# Good
for user in user_list:
    if user.is_active():
        active_users.append(user)

# Bad
active_users = [u for u in user_list if u.is_active()]
```

### 4.2 MongoDB Semantics

- Use descriptive collection and field names:
  - Collection names: **snake_case plural** (e.g., `user_profiles`).
  - Field names: **camelCase** (to match MongoDB standards).

```json
{
    "_id": "123456",
    "userName": "johndoe",
    "profileSettings": {
        "theme": "dark",
        "notificationsEnabled": true
    }
}
```

### 4.3 Logging

- Use Python's `logging` module:
  - Log at appropriate levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
  - Include timestamps and context:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### 4.4 Guard Clauses

- Use guard clauses to simplify complex conditional logic:

```python
def process_user(user):
    if not user.is_active():
        return
    # Process active user
    ...
```

- As compared to:

```python
def process_user(user):
    if user.is_active():
        # Process active user
        ...
```

### 4.5 Helper Methods

- Use helper methods to break down complex algorithms into smaller, manageable pieces, especially for methods with many tab scopes:

```python
def complex_algorithm(data):
    result = step_one(data)
    result = step_two(result)
    return step_three(result)

def step_one(data):
    # Perform first step
    ...

def step_two(data):
    # Perform second step
    ...

def step_three(data):
    # Perform third step
    ...
```

### 4.6 Error Handling

- Catch specific exceptions, log meaningful messages, and use `raise` to propagate errors:

```python
try:
    db.connect()
except ConnectionError as e:
    logging.error(f"Database connection failed: {e}")
    raise
```

- Example:

```python
def fetch_user_data(user_id: str) -> dict:
    try:
        user_data = db.get_user(user_id)
        if not user_data:
            raise ValueError(f"No user found with ID: {user_id}")
        return user_data
    except Exception as e:
        logging.error(f"Error fetching user data: {e}")
        raise
```

### 4.7 Database Usage

- Database should only be called from the context of the bot (e.g., `self.bot.db`). Never instantiate another db, and db should not be used for utility methods:

```python
class UserProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def get_profile(self, ctx, user_id: str):
        user_profile = self.bot.db.get_user(user_id)
        await ctx.send(user_profile)
```

---

## 5. Managing Dependencies

### 5.1 Dependency Management

- Use a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 5.2 Installing Requirements

- Use `requirements.txt` for production dependencies and `requirements_dev.txt` for development dependencies:

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements_dev.txt
```

### 5.3 requirements.txt vs requirements_dev.txt

- `requirements.txt`: Contains the dependencies required for the application to run in production.
- `requirements_dev.txt`: Contains additional dependencies required for development, such as testing and linting tools.

Example `requirements.txt`:

```plaintext
discord.py
pymongo
```

Example `requirements_dev.txt`:

```plaintext
pytest
flake8
black
mypy
```

---

## 6. Imports

### 6.1 Minimize Imports

- Minimize the use of `from library import a, b, c, d`. Instead, import the entire module and use it with the module name to avoid namespace conflicts:

```python
# Good
import os
import sys

# Bad
from os import path, mkdir, remove
from sys import argv, exit
```

### 6.2 Import Order

- Follow the standard import order: standard library imports, third-party imports, and local imports. Separate each group with a blank line:

```python
# Standard library imports
import os
import sys

# Third-party imports
import requests

# Local imports
from .utils import helper_function
```

---

## 7. Module Initialization

### 7.1 Creating `__init__.py` Files

- When adding new scripts to a module, ensure that the module's directory contains an `__init__.py` file. This file can be empty or used to initialize the module.

---

## 8. Pre-Push Checklist

Before pushing your code to the repository, ensure the following steps are completed:

### 8.1 Code Formatting with Black

- Use **black** to automatically format your code files:

```bash
# Install black if not already installed
pip install black

# Format your code files
black path/to/your/code/file.py
```

### 8.2 Linting with Flake8

- Use **flake8** to check for style guide enforcement and code quality issues in your code files:

```bash
# Install flake8 if not already installed
pip install flake8

# Run flake8 on your code files
flake8 path/to/your/code/file.py
```

### 8.3 Type Checking with Mypy

- Use **mypy** for static type checking in your code files:

```bash
# Install mypy if not already installed
pip install mypy

# Run mypy on your code files
mypy path/to/your/code/file.py
```

### 8.4 Running Tests with Pytest

- Use **pytest** for running unit tests:

```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest
```

### 8.5 Pushing to the Repository

- Ensure all tests pass and code is properly formatted and linted before pushing:

```bash
# Add changes to the staging area
git add .

# Commit changes with a descriptive message
git commit -m "[Description of changes]"

# Push changes to the repository
git push origin [branch-name]
```

- Use descriptive commit messages:

```plaintext
[Feature] Add user profile creation functionality
[Fix] Resolve MongoDB connection issue
```

---

## 9. Pull Request Guidelines

- Include a clear description of changes.
- Link to relevant issues.
- Request at least one reviewer for approval.

---
