# Quick Start Guide - Polling Booth Bulk Upload API

## Installation

```bash
# 1. Install dependencies
cd backend
pip install -r requirements.txt

# 2. Run migrations (if needed)
python manage.py migrate

# 3. Start server
python manage.py runserver
```

## Quick Reference

### Endpoints
```
POST   /api/polling-booths/bulk-upload/  - Upload CSV/Excel (Admin+)
GET    /api/polling-booths/template/     - Download template (Any user)
GET    /api/polling-booths/               - List booths (Any user)
GET    /api/polling-booths/{id}/          - Get booth (Any user)
POST   /api/polling-booths/               - Create booth (Admin+)
PATCH  /api/polling-booths/{id}/          - Update booth (Manager+)
DELETE /api/polling-booths/{id}/          - Delete booth (Manager+)
GET    /api/polling-booths/stats/         - Get statistics (Any user)
```

### Quick Upload (cURL)

```bash
# Download template
curl -X GET http://localhost:8000/api/polling-booths/template/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o template.csv

# Upload CSV
curl -X POST http://localhost:8000/api/polling-booths/bulk-upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@my_booths.csv"
```

### Python Upload

```python
import requests

url = "http://localhost:8000/api/polling-booths/bulk-upload/"
headers = {"Authorization": "Bearer YOUR_TOKEN"}
files = {"file": open("booths.csv", "rb")}

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### Required CSV Columns

```csv
booth_number,name,state_code,district_code,constituency_code
001,School Name,TN,TN001,TN001
002,Community Hall,TN,TN001,TN001
```

### Optional Columns
- building_name, address, area, landmark, pincode
- latitude, longitude
- total_voters, male_voters, female_voters, other_voters
- is_active, is_accessible

## Permissions

| Role | Read | Create | Update | Delete |
|------|------|--------|--------|--------|
| Superadmin | All | Yes | Yes | Yes |
| Admin | State | Yes | Yes | Yes |
| Manager | District | No | Yes | Yes |
| Analyst | Constituency | No | No | No |
| User | Ward | No | No | No |

## File Limits

- **Max file size**: 10 MB
- **Max rows**: 10,000 per upload
- **Formats**: .csv, .xlsx, .xls

## Common Issues

### "Missing required columns"
→ Ensure CSV has: booth_number, name, state_code, district_code, constituency_code

### "Invalid state_code"
→ Get valid codes: `curl -X GET http://localhost:8000/api/states/`

### "Permission denied"
→ Need Admin role for bulk upload, Manager role for updates

### "File too large"
→ Split into smaller files (< 10 MB each)

## Response Format

### Success
```json
{
  "success": true,
  "message": "Successfully processed 95 booths. 5 failed.",
  "total_rows": 100,
  "success_count": 95,
  "failed_count": 5,
  "errors": [
    {"row": 12, "error": "Invalid state_code", "data": {...}}
  ]
}
```

### Error
```json
{
  "success": false,
  "error": "Missing required columns: state_code"
}
```

## Testing

```bash
# Run tests
python manage.py test tests.test_polling_booth_upload

# Test specific case
python manage.py test tests.test_polling_booth_upload.PollingBoothBulkUploadTestCase.test_bulk_upload_success
```

## Documentation

- **Full API Docs**: `/backend/docs/POLLING_BOOTH_BULK_UPLOAD.md`
- **Implementation Summary**: `/POLLING_BOOTH_IMPLEMENTATION_SUMMARY.md`
- **Test Cases**: `/backend/tests/test_polling_booth_upload.py`

## Need Help?

1. Download the template first
2. Check error messages in response
3. Verify state/district/constituency codes exist
4. Test with small file (10 rows) first
5. Review full documentation

---

**Quick Command Summary**
```bash
# Download template
GET /api/polling-booths/template/

# Upload file
POST /api/polling-booths/bulk-upload/
Body: file=@booths.csv

# Check stats
GET /api/polling-booths/stats/

# List booths
GET /api/polling-booths/
```
