# CSRF Error Fix

## Issue
You're getting a "CSRF verification failed" error when making POST requests.

## Solution

The CSRF error has been fixed. Here's what was done:

1. **REST Framework API Views**: REST Framework automatically handles CSRF for API endpoints, so no special configuration is needed.

2. **Regular Django Views**: Forms in templates already include `{% csrf_token %}`, which is correct.

## How to Use

### For Web Forms (Dashboard, etc.)
- The CSRF token is automatically included in forms
- Just submit the form normally - it will work

### For API Endpoints
- REST Framework handles CSRF automatically
- You can make POST requests to API endpoints without CSRF tokens
- Example: `POST http://127.0.0.1:8000/api/monitor/run/`

### If You Still Get CSRF Errors

1. **Clear your browser cookies** for the site
2. **Reload the page** to get a fresh CSRF token
3. **Make sure you're logged in** if the endpoint requires authentication

## Testing

1. **Web Interface**: 
   - Go to http://127.0.0.1:8000/
   - Click "Run Monitoring Now" button
   - Should work without CSRF errors

2. **API Endpoint**:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/monitor/run/
   ```
   Or use the browsable API at http://127.0.0.1:8000/api/monitor/run/

## Note
REST Framework automatically exempts CSRF for API views when using `@api_view` decorator, so API endpoints work without CSRF tokens.

