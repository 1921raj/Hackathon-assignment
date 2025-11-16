# API Testing Guide

## Quick Start

1. **Start the Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Run the test script:**
   ```bash
   python test_api.py
   ```

3. **Or test manually in browser:**
   - Open: http://127.0.0.1:8000/api/
   - This shows the browsable API interface

## Manual Testing

### Test Dashboard Stats
```
GET http://127.0.0.1:8000/api/dashboard/stats/
```

### Test Competitors
```
GET http://127.0.0.1:8000/api/competitors/
GET http://127.0.0.1:8000/api/competitors/?is_active=true
```

### Test Updates
```
GET http://127.0.0.1:8000/api/updates/
GET http://127.0.0.1:8000/api/updates/?high_impact=true
GET http://127.0.0.1:8000/api/updates/?days=7
GET http://127.0.0.1:8000/api/updates/?type=pricing
```

### Test Trends
```
GET http://127.0.0.1:8000/api/trends/
POST http://127.0.0.1:8000/api/trends/analyze/
```

### Test Monitoring
```
POST http://127.0.0.1:8000/api/monitor/run/
```

## Expected Results

All endpoints should return:
- **Status Code:** 200 (OK) or 201 (Created)
- **Content-Type:** application/json
- **Valid JSON** with appropriate data structure

See `API_DOCUMENTATION.md` for detailed response formats.

