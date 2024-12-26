# SpoofCaller - Spam Detection and User Management

## Overview
SpoofCaller is a Django-based application designed to manage user data and detect spam phone numbers. It allows users to report spam numbers, search for people by name or phone number, and check the likelihood of a phone number being spam. The app is designed with user authentication and includes a management command to populate the database with fake data for testing.

## Features
- **User Authentication**: Users can register and log in using JWT authentication.
- **Spam Reporting**: Users can mark phone numbers as spam.
- **User Search**: Users can search for people by name or phone number, with search results including the phone number and spam likelihood.
- **Spam Counter**: Users can see how many spam reports exist for a specific phone number.
- **Detailed User Information**: Users can view detailed information about a person, including their spam likelihood and contact information, based on their search query.

## Requirements
- Python 3.8+
- Django 3.2+
- Django REST Framework
- SimpleJWT for authentication
- Faker (for generating fake data)
- PostgreSQL (or your preferred database)

## Installation

### 1. Create a virtual environment

Create and activate a virtual environment to isolate your project dependencies.

```bash
python3 -m venv .venv
source .venv/bin/activate  # For Linux/MacOS
.venv\Scripts\activate     # For Windows
```
### 2. Install dependencies
Install the required Python packages listed in requirements.txt.

```bash
pip install -r requirements.txt
```

### 3. Set up the database

Run the migrations to set up the database schema.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Populate the database with fake data
```bash
python manage.py populate_fake_data
```
This will create fake users, contacts, and spam reports in the database.

### 5. Start the development server
Start the Django development server to run the app locally.
```bash
python manage.py runserver
```

## API Endpoints

The following endpoints are available for interacting with the app:
### 1. Authentication

    POST /api/register/: Register a new user.
    POST /api/login/: Log in to get an access token (JWT).
    POST /api/logout/: Log out by invalidating the access token.

### 2. Spam Reporting

    POST /api/mark-spam/: Mark a phone number as spam. Requires authentication.

### 3. Search API

    GET /api/search-by-name/: Search for people by name. Returns matching users and contacts. Requires authentication.
    GET /api/search-by-phone/: Search for people by phone number. Returns matching results from both users and contacts. Requires authentication.
    GET /api/search-name/: Search for people by name, with results ordered based on exact matches. Requires authentication.
    GET /api/spam-counter/: Check the number of spam reports for a given phone number. Requires authentication.
    GET /api/display-detail/: View detailed information about a person by phone number.

