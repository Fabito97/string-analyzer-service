# String Analyzer API

This is a RESTful API service built with FastAPI that analyzes strings, computes various properties, and stores them for later retrieval in a SQLite database.

## Features

*   Analyzes strings for properties like length, palindrome status, word count, and character frequency.
*   Stores analysis results, ensuring each unique string is saved only once.
*   Provides RESTful endpoints to create, retrieve, filter, and delete string analyses.
*   Includes a natural language query endpoint for intuitive filtering (e.g., "single word palindromes").

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites

*   Python 3.8+

### 2. Clone the Repository

First, clone the repository to your local machine.

```sh
git clone <your-repo-url>
cd <repository-folder-name>
```

### 3. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies and avoid conflicts with other projects.

**On Windows:**
```sh
python -m venv .venv
.\.venv\Scripts\activate
```

**On macOS/Linux:**
```sh
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies

Install all the required packages using the `requirements.txt` file.

```sh
pip install -r requirements.txt
```

## Running the Application Locally

Once the setup is complete, you can run the application using `uvicorn`, a lightning-fast ASGI server.

```sh
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

The `--reload` flag makes the server restart automatically after you make code changes, which is useful for development. When you first run the application, a `sql_app.db` file will be created in the project root. This is the SQLite database file.

## API Endpoints

The interactive API documentation (powered by Swagger UI) is available at `http://127.0.0.1:8000/docs`. You can use this interface to test all the endpoints directly from your browser.

---

### 1. Create/Analyze String

Analyzes a new string and stores its properties.

*   **URL:** `/strings`
*   **Method:** `POST`
*   **Request Body:**
    ```json
    {
      "value": "your string to analyze"
    }
    ```
*   **Success Response (201 Created):**
    Returns the full analysis object, including its unique ID (SHA256 hash) and computed properties.
    ```json
    {
      "id": "f2e21239d...c89a",
      "value": "A man a plan a canal Panama",
      "properties": {
        "length": 27,
        "is_palindrome": true,
        "unique_characters": 9,
        "word_count": 7,
        "sha256_hash": "f2e21239d...c89a",
        "character_frequency_map": { "a": 8, " ": 6, "m": 2, "n": 3, "p": 1, "l": 2, "c": 1 }
      },
      "created_at": "2023-10-28T10:00:00Z"
    }
    ```
*   **Error Responses:**
    *   `409 Conflict`: If the string already exists in the database.
    *   `422 Unprocessable Entity`: If the `value` field is not a string.

---

### 2. Get Specific String

Retrieves the stored analysis for a specific string.

*   **URL:** `/strings/{string_value}`
*   **Method:** `GET`
*   **Success Response (200 OK):**
    Returns the analysis object for the requested string.
*   **Error Response:**
    *   `404 Not Found`: If the string does not exist in the database.

---

### 3. Get All Strings with Filtering

Retrieves a list of all stored strings, with optional query parameters for filtering.

*   **URL:** `/strings`
*   **Method:** `GET`
*   **Query Parameters:**
    *   `is_palindrome` (boolean, e.g., `true`)
    *   `min_length` (integer, e.g., `5`)
    *   `max_length` (integer, e.g., `20`)
    *   `word_count` (integer, e.g., `1`)
    *   `contains_character` (string, single character, e.g., `z`)
*   **Example:** `/strings?is_palindrome=true&min_length=3`
*   **Success Response (200 OK):**
    ```json
    {
      "data": [ /* array of string analysis objects */ ],
      "count": 3,
      "filters_applied": {
        "is_palindrome": true,
        "min_length": 3
      }
    }
    ```

---

### 4. Natural Language Filtering

Filters strings based on a human-readable query.

*   **URL:** `/strings/filter-by-natural-language`
*   **Method:** `GET`
*   **Query Parameter:**
    *   `query` (string): A natural language query.
*   **Supported Query Examples:**
    *   `"all single word palindromic strings"`
    *   `"strings longer than 10 characters"`
    *   `"strings containing the letter z"`
*   **Success Response (200 OK):**
    ```json
    {
      "data": [ /* array of matching string analysis objects */ ],
      "count": 1,
      "interpreted_query": {
        "original": "all single word palindromic strings",
        "parsed_filters": {
          "word_count": 1,
          "is_palindrome": true
        }
      }
    }
    ```
*   **Error Responses:**
    *   `400 Bad Request`: If the query cannot be parsed.

---

### 5. Delete String

Deletes a string and its analysis from the database.

*   **URL:** `/strings/{string_value}`
*   **Method:** `DELETE`
*   **Success Response:** `204 No Content` (empty response body)
*   **Error Response:**
    *   `404 Not Found`: If the string does not exist.
