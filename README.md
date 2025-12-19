# CAS Lookup API

A FastAPI application that looks up CAS (Chemical Abstracts Service) numbers for chemical compounds from The Good Scents Company database.

## Features

- Single POST endpoint `/lookup-cas` that accepts a compound name
- Input validation using Pydantic
- Web scraping from https://www.thegoodscentscompany.com/allproc-1.html
- Async HTTP requests with httpx
- Interactive API documentation at `/docs`

## Setup

This project uses [uv](https://github.com/astral-sh/uv) for package management.

### Install dependencies

```bash
uv sync
```

## Running the Application

### Development server

```bash
uv run uvicorn main:app --reload
```

The API will be available at http://localhost:8000

### Or run directly

```bash
uv run python main.py
```

## API Endpoints

### GET /

Root endpoint with API information.

### POST /lookup-cas

Lookup CAS number for a given compound name.

**Request Body:**
```json
{
  "compound_name": "formaldehyde"
}
```

**Response:**
```json
{
  "compound_name": "formaldehyde",
  "cas_number": "50-00-0",
  "message": "CAS number found successfully"
}
```

### GET /docs

Interactive API documentation (Swagger UI).

## Example Usage

### Using curl

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "lactic acid"}'
```

### Using Python

```python
import httpx

response = httpx.post(
    "http://localhost:8000/lookup-cas",
    json={"compound_name": "lactic acid"}
)
print(response.json())
```

## Input Validation

The API validates:
- Compound name must be between 1 and 200 characters
- Compound name cannot be empty or only whitespace
- Invalid requests return 422 Unprocessable Entity with error details

## Dependencies

- fastapi: Web framework
- uvicorn: ASGI server
- httpx: Async HTTP client
- beautifulsoup4: HTML parsing
- pydantic: Data validation