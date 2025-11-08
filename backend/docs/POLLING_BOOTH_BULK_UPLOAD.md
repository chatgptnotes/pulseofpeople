# Polling Booth Bulk Upload API Documentation

## Overview
The Polling Booth Bulk Upload API allows administrators to efficiently upload large numbers of polling booth data via CSV or Excel files. This feature includes role-based permissions, data isolation, validation, and comprehensive error reporting.

## API Endpoints

### 1. Bulk Upload Polling Booths
**Endpoint:** `POST /api/polling-booths/bulk-upload/`
**Authentication:** Required (JWT Token)
**Permission:** Admin and above
**Content-Type:** `multipart/form-data`

#### Request
```bash
curl -X POST http://localhost:8000/api/polling-booths/bulk-upload/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@polling_booths.csv"
```

#### Response (Success)
```json
{
  "success": true,
  "message": "Successfully processed 95 booths. 5 failed.",
  "total_rows": 100,
  "success_count": 95,
  "failed_count": 5,
  "errors": [
    {
      "row": 12,
      "error": "State 'XY' not found",
      "data": {"booth_number": "012", "name": "Test Booth", ...}
    }
  ]
}
```

#### Response (Error)
```json
{
  "success": false,
  "error": "Missing required columns: state_code, district_code",
  "required_columns": ["booth_number", "name", "state_code", "district_code", "constituency_code"],
  "found_columns": ["booth_number", "name"]
}
```

### 2. Download CSV Template
**Endpoint:** `GET /api/polling-booths/template/`
**Authentication:** Required
**Permission:** Any authenticated user

#### Request
```bash
curl -X GET http://localhost:8000/api/polling-booths/template/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o polling_booth_template.csv
```

Returns a CSV file with headers and sample data.

### 3. List Polling Booths
**Endpoint:** `GET /api/polling-booths/`
**Authentication:** Required
**Permission:** Any authenticated user (data filtered by role)

#### Request
```bash
curl -X GET http://localhost:8000/api/polling-booths/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### Response
```json
{
  "count": 150,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "booth_number": "001",
      "name": "Government High School, Main Road",
      "area": "Anna Nagar",
      "constituency_name": "Chennai Central",
      "total_voters": 1200
    }
  ]
}
```

### 4. Get Polling Booth Details
**Endpoint:** `GET /api/polling-booths/{id}/`
**Authentication:** Required
**Permission:** Any authenticated user (with data isolation)

#### Response
```json
{
  "id": 1,
  "booth_number": "001",
  "name": "Government High School, Main Road",
  "building_name": "Government High School",
  "state": 1,
  "state_name": "Tamil Nadu",
  "district": 5,
  "district_name": "Chennai",
  "constituency": 10,
  "constituency_name": "Chennai Central",
  "address": "123 Main Road, Chennai",
  "area": "Anna Nagar",
  "landmark": "Near Bus Stand",
  "pincode": "600001",
  "latitude": "13.082680",
  "longitude": "80.270718",
  "total_voters": 1200,
  "male_voters": 600,
  "female_voters": 580,
  "other_voters": 20,
  "is_active": true,
  "is_accessible": true,
  "metadata": {},
  "created_at": "2025-11-08T10:00:00Z",
  "updated_at": "2025-11-08T10:00:00Z"
}
```

### 5. Update Polling Booth
**Endpoint:** `PUT /api/polling-booths/{id}/` or `PATCH /api/polling-booths/{id}/`
**Authentication:** Required
**Permission:** Manager and above

#### Request (PATCH)
```bash
curl -X PATCH http://localhost:8000/api/polling-booths/1/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "total_voters": 1250,
    "is_accessible": true
  }'
```

### 6. Delete Polling Booth
**Endpoint:** `DELETE /api/polling-booths/{id}/`
**Authentication:** Required
**Permission:** Manager and above

#### Request
```bash
curl -X DELETE http://localhost:8000/api/polling-booths/1/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 7. Get Polling Booth Statistics
**Endpoint:** `GET /api/polling-booths/stats/`
**Authentication:** Required
**Permission:** Any authenticated user (data filtered by role)

#### Response
```json
{
  "total_booths": 234,
  "active_booths": 230,
  "accessible_booths": 210,
  "total_voters": 280000,
  "by_constituency": {
    "Chennai Central": {
      "booths": 45,
      "voters": 54000
    },
    "Chennai North": {
      "booths": 50,
      "voters": 60000
    }
  }
}
```

## CSV File Format

### Required Columns
- **booth_number** (string): Official booth number (e.g., '001', '002A')
- **name** (string): Polling booth name/location
- **state_code** (string): State code (e.g., 'TN' for Tamil Nadu)
- **district_code** (string): District code (e.g., 'TN001')
- **constituency_code** (string): Constituency code (e.g., 'TN001')

### Optional Columns
- **building_name** (string): School/building name
- **address** (string): Full address
- **area** (string): Locality/area name
- **landmark** (string): Nearby landmark
- **pincode** (string): PIN code
- **latitude** (decimal): Geographic latitude
- **longitude** (decimal): Geographic longitude
- **total_voters** (integer): Total registered voters (default: 0)
- **male_voters** (integer): Male voters (default: 0)
- **female_voters** (integer): Female voters (default: 0)
- **other_voters** (integer): Other gender voters (default: 0)
- **is_active** (boolean): Active status (default: True)
- **is_accessible** (boolean): Wheelchair accessible (default: True)

### Sample CSV
```csv
booth_number,name,state_code,district_code,constituency_code,building_name,address,area,landmark,pincode,latitude,longitude,total_voters,male_voters,female_voters,other_voters,is_active,is_accessible
001,Government High School Main Road,TN,TN001,TN001,Government High School,123 Main Road Chennai,Anna Nagar,Near Bus Stand,600001,13.082680,80.270718,1200,600,580,20,True,True
002,Corporation Primary School West Street,TN,TN001,TN001,Corporation Primary School,456 West Street Chennai,Anna Nagar West,Near Park,600001,13.082123,80.271234,1500,750,730,20,True,True
003A,Community Hall East Avenue,TN,TN001,TN001,Community Hall,789 East Avenue Chennai,Anna Nagar East,Near Temple,600001,,,800,400,390,10,True,False
```

### Excel Format
Excel files (.xlsx, .xls) are also supported with the same column structure.

## Permission Rules

### Create/Upload (POST)
- **Admin** and above can bulk upload polling booths
- Any admin can create booths in any location

### Read (GET)
All authenticated users can read, with data isolation:
- **Superadmin**: sees all booths nationwide
- **Admin**: sees booths in their assigned state
- **Manager**: sees booths in their assigned district
- **Analyst**: sees booths in their assigned constituency
- **User**: sees booths in their assigned ward/constituency
- **Viewer/Volunteer**: sees booths in their assigned district

### Update (PUT/PATCH)
- **Manager** and above can update polling booths
- Updates respect data isolation rules

### Delete (DELETE)
- **Manager** and above can delete polling booths
- Deletions respect data isolation rules

## Data Validation

### File Validation
- **File Types**: CSV (.csv), Excel (.xlsx, .xls)
- **Maximum File Size**: 10 MB
- **Maximum Rows**: 10,000 rows per upload
- **Encoding**: UTF-8 (for CSV)

### Data Validation
1. **Required Fields**: booth_number, name, state_code, district_code, constituency_code must not be empty
2. **Foreign Keys**: state_code, district_code, constituency_code must exist in the database
3. **Duplicates**: If booth_number already exists in the constituency, the existing booth will be updated
4. **Data Types**: Numeric fields (voters, coordinates) are validated for correct format
5. **Boolean Fields**: Accepts True/False, 1/0, Yes/No

### Error Handling
- Row-level validation with detailed error messages
- Up to 100 errors returned in response
- Successful rows are processed even if some rows fail
- Transactional integrity maintained

## Usage Examples

### Python (requests)
```python
import requests

# Upload CSV file
url = "http://localhost:8000/api/polling-booths/bulk-upload/"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}
files = {
    "file": open("polling_booths.csv", "rb")
}

response = requests.post(url, headers=headers, files=files)
result = response.json()

print(f"Success: {result['success_count']}, Failed: {result['failed_count']}")
for error in result['errors']:
    print(f"Row {error['row']}: {error['error']}")
```

### JavaScript (fetch)
```javascript
const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('/api/polling-booths/bulk-upload/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });

  const result = await response.json();
  console.log(`Success: ${result.success_count}, Failed: ${result.failed_count}`);

  if (result.errors.length > 0) {
    result.errors.forEach(error => {
      console.error(`Row ${error.row}: ${error.error}`);
    });
  }
};
```

### cURL
```bash
# Upload CSV
curl -X POST http://localhost:8000/api/polling-booths/bulk-upload/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@polling_booths.csv"

# Download template
curl -X GET http://localhost:8000/api/polling-booths/template/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -o template.csv

# Get statistics
curl -X GET http://localhost:8000/api/polling-booths/stats/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Best Practices

1. **Download Template First**: Always download the template to ensure correct column names and format
2. **Validate Data**: Validate state/district/constituency codes exist before uploading
3. **Batch Uploads**: Split large datasets into multiple uploads of 5,000 rows each for better performance
4. **Error Review**: Review all errors carefully and fix data before re-uploading
5. **Test Upload**: Test with a small file (10-20 rows) before uploading full dataset
6. **Backup Data**: Keep original data files as backup
7. **Update vs Create**: Use the same booth_number for updates; system will automatically update existing booths

## Troubleshooting

### Common Errors

#### "Missing required columns"
- Ensure CSV has all required columns: booth_number, name, state_code, district_code, constituency_code
- Check for typos in column names (case-sensitive)

#### "Invalid state_code: XY"
- State code doesn't exist in database
- Verify state codes using `GET /api/states/`

#### "File too large"
- File exceeds 10 MB limit
- Split file into smaller batches

#### "Too many rows"
- File has more than 10,000 rows
- Split into multiple files

#### "Invalid file type"
- Only .csv, .xlsx, .xls files are accepted
- Ensure file has correct extension

## Performance Considerations

- **Processing Time**: ~1-2 seconds per 100 rows
- **Database Caching**: State/district/constituency data is cached for fast lookups
- **Concurrent Uploads**: System supports multiple simultaneous uploads by different users
- **Transaction Safety**: Failed uploads don't affect database integrity

## Dependencies

The bulk upload feature requires the following Python packages:
- `pandas==2.2.0` - DataFrame processing
- `openpyxl==3.1.2` - Excel file support

These are automatically installed via `requirements.txt`.

## Security

- **Authentication Required**: All endpoints require valid JWT token
- **Role-Based Access**: Permissions enforced at view level
- **Data Isolation**: Users only see data within their jurisdiction
- **File Validation**: File type and size validated before processing
- **SQL Injection Prevention**: Django ORM protects against SQL injection
- **Rate Limiting**: Consider implementing rate limiting for production use

## Support

For issues or questions:
1. Check error messages in upload response
2. Verify data format matches template
3. Test with small sample file
4. Contact system administrator for database-level issues
