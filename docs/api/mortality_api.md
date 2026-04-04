# Mortality API Reference

## Endpoints

### GET /api/v1/mortality

Returns all mortality records.

**Parameters:**
- `limit` (int): Max results (default: 100)
- `offset` (int): Pagination offset
- `filter` (string): Filter expression

### POST /api/v1/mortality

Create a new mortality record.

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "metadata": {}
}
```

### GET /api/v1/mortality/{id}

Get mortality by ID.

### DELETE /api/v1/mortality/{id}

Delete mortality record.
