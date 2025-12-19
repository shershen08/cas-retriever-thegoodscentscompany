# API Examples

## Starting the Server

```bash
uv run uvicorn main:app --reload
```

Or:

```bash
uv run python main.py
```

## Example Requests

### Successful Lookup

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "formaldehyde"}'
```

Response:
```json
{
  "compound_name": "formaldehyde",
  "cas_number": "50-00-0",
  "message": "CAS number found successfully"
}
```

### Another Example - Lactic Acid

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "lactic acid"}'
```

Response:
```json
{
  "compound_name": "lactic acid",
  "cas_number": "50-21-5",
  "message": "CAS number found successfully"
}
```

### Compound Not Found

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "unknown compound xyz"}'
```

Response:
```json
{
  "compound_name": "unknown compound xyz",
  "cas_number": null,
  "message": "CAS number not found for the given compound"
}
```

### Invalid Input - Empty String

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": ""}'
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "compound_name"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {
        "min_length": 1
      }
    }
  ]
}
```

### Invalid Input - Only Whitespace

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "   "}'
```

Response (422 Unprocessable Entity):
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "compound_name"],
      "msg": "Value error, Compound name cannot be empty or only whitespace",
      "input": "   "
    }
  ]
}
```

### Invalid Input - Too Long

```bash
curl -X POST "http://localhost:8000/lookup-cas" \
  -H "Content-Type: application/json" \
  -d '{"compound_name": "a very long string that exceeds 200 characters..."}'
```

Response (422 Unprocessable Entity): Error indicating max length exceeded

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test the API directly in your browser.
