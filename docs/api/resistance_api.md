# Resistance API Reference

## Endpoints

### GET /api/v1/resistance

Returns all resistance records.

**Parameters:**
- `limit` (int): Max results (default: 100)
- `offset` (int): Pagination offset
- `filter` (string): Filter expression

### POST /api/v1/resistance

Create a new resistance record.

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "metadata": {}
}
```

### GET /api/v1/resistance/{id}

Get resistance by ID.

### DELETE /api/v1/resistance/{id}

Delete resistance record.
