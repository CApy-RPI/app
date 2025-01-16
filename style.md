# Coding Style Guide for Python Discord Bot with MongoDB

## 1. Code Structure and Organization

### 1.1 Folder Structure

Maintain a clear, modular folder layout:

```plaintext
discord_bot/
├── src/
│   ├── cogs/                  # Separate modules for bot commands/features
│   ├── db/                    # Database models and connection utilities
│   ├── modules/               # Additional modules for extended functionalities
│   ├── resources/             # Static resources like images, JSON files, etc.
│   ├── utils/                 # Utility/helper functions
│   ├── config.py              # Configuration file
│   └── main.py                # Entry point of the bot
├── tests/                     # Unit and integration tests
├── .env                       # Environment variables
├── requirements.txt           # Python dependencies
├── style.md                   # Coding style guide
├── test.md                    # Testing script
└── updater.py                 # Script for updating host
```

### 1.2 Code Structure

- Use a class-based design for modularity:
  - Define a `Cog` for each bot feature (e.g., moderation, profiles).
  - Separate utility methods by category into individual files for clarity.

---

## 2. Naming Conventions

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

## 5. Code Review and Version Control

### 5.1 Git Commit Standards

- Use descriptive commit messages:

```plaintext
[Feature] Add user profile creation functionality
[Fix] Resolve MongoDB connection issue
```

### 5.2 Pull Request Guidelines

- Include a clear description of changes.
- Link to relevant issues.
- Request at least one reviewer for approval.

### 5.3 Mandatory Testing and Formatting

- Ensure all tests pass and code is formatted before committing:

```bash
py test.py
black ${filename}
```

---

## 6. Development Practices

### 6.1 Testing

- Use **pytest** for unit testing.

```python
def test_user_profile_creation():
    # Arrange
    test_user_id = "123"
    test_data = {"name": "Jane Doe"}

    # Act
    db.create_user(test_user_id, test_data)

    # Assert
    assert db.get_user(test_user_id)["name"] == "Jane Doe"
```

### 6.2 Configurations

- Store sensitive data (e.g., tokens, database credentials) in environment variables or `.env` files.
- **Never** hard-code or link any sensitive data to any file that will be uploaded.

### 6.3 Dependency Management

- Use a virtual environment to manage dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 6.4 Code Formatting

- Use **black** for automatic code formatting:

```bash
black .
```

---
