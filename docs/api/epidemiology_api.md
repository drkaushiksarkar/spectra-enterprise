# Epidemiology API Reference

## Endpoints

### GET /api/v1/epidemiology

Returns all epidemiology records.

**Parameters:**
- `limit` (int): Max results (default: 100)
- `offset` (int): Pagination offset
- `filter` (string): Filter expression

### POST /api/v1/epidemiology

Create a new epidemiology record.

**Request Body:**
```json
{
  "name": "string",
  "type": "string",
  "metadata": {}
}
```

### GET /api/v1/epidemiology/{id}

Get epidemiology by ID.

### DELETE /api/v1/epidemiology/{id}

Delete epidemiology record.
