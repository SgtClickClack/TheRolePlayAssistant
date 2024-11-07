# API Documentation

## Base URL 

## Authentication

### **Register User**

- **Endpoint:** `/auth/register`
- **Method:** `POST`
- **Description:** Registers a new user.
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Responses:**
  - `201 Created`: User registered successfully.
  - `400 Bad Request`: Username already exists.
  - `500 Internal Server Error`: Server error.

### **Login User**

- **Endpoint:** `/auth/login`
- **Method:** `POST`
- **Description:** Authenticates a user and returns a JWT token.
- **Request Body:**
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Responses:**
  - `200 OK`: Returns JWT token.
    ```json
    {
      "token": "jwt_token_here"
    }
    ```
  - `400 Bad Request`: Invalid credentials.
  - `500 Internal Server Error`: Server error.

## Feedback

### **Submit Feedback**

- **Endpoint:** `/feedback`
- **Method:** `POST`
- **Description:** Submits user feedback for generated text.
- **Headers:**
  - `Authorization: Bearer <JWT_TOKEN>`
- **Request Body:**
  ```json
  {
    "textId": "string",
    "feedback": 1, // 1 for thumbs up, -1 for thumbs down
    "context": "string" // Optional
  }
  ```
- **Responses:**
  - `201 Created`: Feedback submitted successfully.
  - `400 Bad Request`: Invalid feedback value.
  - `401 Unauthorized`: Missing or invalid token.
  - `500 Internal Server Error`: Server error.

## Metrics

### **Get Feedback Summary**

- **Endpoint:** `/metrics/feedback-summary`
- **Method:** `GET`
- **Description:** Retrieves a summary of feedback counts.
- **Responses:**
  - `200 OK`: Returns feedback summary.
    ```json
    [
      {
        "_id": 1,
        "count": 150
      },
      {
        "_id": -1,
        "count": 30
      }
    ]
    ```
  - `500 Internal Server Error`: Server error.