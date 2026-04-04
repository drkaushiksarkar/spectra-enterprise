# Surveillance API Reference

## Endpoints

### GET /api/v1/surveillance

Returns all surveillance records.

**Parameters:**
- `limit` (int): Max results (default: 100)
- `offset` (int): Pagination offset
- `filter` (string): Filter expression

### POST /api/v1/surveillance

Create a new surveillance record.

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "metadata": {}
}
```

### GET /api/v1/surveillance/{id}

Get surveillance by ID.

### DELETE /api/v1/surveillance/{id}

Delete surveillance record.
