# API Documentation

## Base URL
```
http://127.0.0.1:8000/api/
```

## Available Endpoints

### 1. Dashboard Statistics
Get overall statistics for the dashboard.

**Endpoint:** `GET /api/dashboard/stats/`

**Response:**
```json
{
  "total_competitors": 5,
  "total_updates": 120,
  "high_impact_count": 15,
  "recent_week_updates": 25,
  "updates_by_type": {
    "pricing": 30,
    "campaign": 25,
    "release": 20,
    "partnership": 15,
    "feature": 20,
    "news": 10
  }
}
```

---

### 2. Competitors

#### List All Competitors
**Endpoint:** `GET /api/competitors/`

**Query Parameters:**
- `is_active` (optional): Filter by active status (`true`/`false`)

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Competitor Name",
      "website": "https://example.com",
      "description": "Description",
      "industry": "Technology",
      "is_active": true,
      "created_at": "2025-11-15T10:00:00Z",
      "update_count": 25
    }
  ]
}
```

#### Get Single Competitor
**Endpoint:** `GET /api/competitors/{id}/`

---

### 3. Updates

#### List All Updates
**Endpoint:** `GET /api/updates/`

**Query Parameters:**
- `competitor` (optional): Filter by competitor ID
- `type` (optional): Filter by update type (`pricing`, `campaign`, `release`, `partnership`, `feature`, `news`, `other`)
- `high_impact` (optional): Filter high impact updates (`true`/`false`)
- `days` (optional): Get updates from last N days (e.g., `7`)

**Response:**
```json
{
  "count": 120,
  "next": "http://127.0.0.1:8000/api/updates/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "competitor_id": 1,
      "competitor_name": "Competitor Name",
      "title": "Update Title",
      "content": "Update content...",
      "url": "https://example.com/update",
      "update_type": "pricing",
      "detected_at": "2025-11-15T10:00:00Z",
      "published_date": "2025-11-15T09:00:00Z",
      "impact_score": 75,
      "is_high_impact": true,
      "source": "website"
    }
  ]
}
```

#### Get Single Update
**Endpoint:** `GET /api/updates/{id}/`

---

### 4. Trends

#### List All Trends
**Endpoint:** `GET /api/trends/`

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Increase in pricing updates",
      "description": "Detected 10 pricing updates in the last 30 days",
      "trend_type": "pricing",
      "frequency": 10,
      "first_detected": "2025-11-01T10:00:00Z",
      "last_detected": "2025-11-15T10:00:00Z",
      "confidence_score": 0.8,
      "related_updates_count": 10
    }
  ]
}
```

#### Trigger Trend Analysis
**Endpoint:** `POST /api/trends/analyze/`

**Response:**
```json
{
  "message": "Trend analysis completed. Found 3 trends.",
  "trends": [...]
}
```

---

### 5. Notifications

#### List Notifications (Authenticated Users Only)
**Endpoint:** `GET /api/notifications/`

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "update_title": "Update Title",
      "competitor_name": "Competitor Name",
      "message": "High-impact update from Competitor Name: Update Title",
      "is_read": false,
      "created_at": "2025-11-15T10:00:00Z"
    }
  ]
}
```

#### Mark Notification as Read
**Endpoint:** `POST /api/notifications/{id}/mark_read/`

---

### 6. Monitoring

#### Run Competitor Monitoring
**Endpoint:** `POST /api/monitor/run/`

**Response:**
```json
{
  "message": "Monitoring completed",
  "new_updates_count": 5,
  "updates": [...]
}
```

---

## Testing the API

### Using cURL

```bash
# Get dashboard stats
curl http://127.0.0.1:8000/api/dashboard/stats/

# Get all competitors
curl http://127.0.0.1:8000/api/competitors/

# Get high impact updates
curl http://127.0.0.1:8000/api/updates/?high_impact=true

# Run monitoring
curl -X POST http://127.0.0.1:8000/api/monitor/run/
```

### Using Python requests

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Get dashboard stats
response = requests.get(f"{BASE_URL}/dashboard/stats/")
print(response.json())

# Get competitors
response = requests.get(f"{BASE_URL}/competitors/")
print(response.json())

# Get filtered updates
response = requests.get(f"{BASE_URL}/updates/", params={
    'high_impact': 'true',
    'days': '7'
})
print(response.json())
```

### Using Browser

Simply navigate to:
- `http://127.0.0.1:8000/api/` - API root (browsable API)
- `http://127.0.0.1:8000/api/competitors/` - Competitors list
- `http://127.0.0.1:8000/api/updates/` - Updates list
- `http://127.0.0.1:8000/api/dashboard/stats/` - Dashboard stats

The browsable API interface allows you to test endpoints directly in your browser!

---

## Response Format

All endpoints return JSON responses. List endpoints are paginated with 20 items per page.

**Pagination Response:**
```json
{
  "count": 100,
  "next": "http://127.0.0.1:8000/api/updates/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "error": "Invalid request parameters"
}
```

**404 Not Found:**
```json
{
  "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
  "error": "Internal server error"
}
```

