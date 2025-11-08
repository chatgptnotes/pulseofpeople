# Polling Booth Bulk Upload API - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            CLIENT LAYER                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   React UI   │  │ Python SDK   │  │   cURL/CLI   │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
└─────────┼──────────────────┼──────────────────┼──────────────────────────┘
          │                  │                  │
          │   JWT Token      │   JWT Token      │   JWT Token
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼──────────────────────────┐
│                        API GATEWAY (Django URLs)                          │
│  /api/polling-booths/                                                     │
│    ├── bulk-upload/  (POST)    - Upload CSV/Excel                        │
│    ├── template/     (GET)     - Download template                       │
│    ├── stats/        (GET)     - Get statistics                          │
│    ├── /            (GET)     - List booths                              │
│    ├── /{id}/       (GET)     - Get booth details                        │
│    ├── /{id}/       (PATCH)   - Update booth                             │
│    └── /{id}/       (DELETE)  - Delete booth                             │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                     PERMISSION LAYER (DRF Permissions)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  CanManagePollingBooths                                             │ │
│  │  ├── GET:    IsAuthenticated (Any user)                            │ │
│  │  ├── POST:   IsAdminOrAbove (Admin, Superadmin)                    │ │
│  │  ├── PATCH:  IsManagerOrAbove (Manager, Admin, Superadmin)         │ │
│  │  └── DELETE: IsManagerOrAbove (Manager, Admin, Superadmin)         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                      VIEW LAYER (PollingBoothViewSet)                     │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Data Isolation Filter (get_queryset)                              │ │
│  │  ├── Superadmin:  All booths                                       │ │
│  │  ├── Admin:       Booths in assigned_state                         │ │
│  │  ├── Manager:     Booths in assigned_district                      │ │
│  │  ├── Analyst:     Booths in constituency (text match)              │ │
│  │  ├── User:        Booths in constituency/city                      │ │
│  │  └── Other:       Booths in assigned_district                      │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Bulk Upload Handler (_process_bulk_upload)                        │ │
│  │  ├── 1. Parse CSV/Excel (pandas)                                   │ │
│  │  ├── 2. Validate columns                                           │ │
│  │  ├── 3. Validate row count (max 10,000)                            │ │
│  │  ├── 4. Cache foreign key lookups                                  │ │
│  │  ├── 5. Process rows with validation                               │ │
│  │  ├── 6. Update existing or create new                              │ │
│  │  └── 7. Return success/error report                                │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                    SERIALIZER LAYER (DRF Serializers)                     │
│  ┌────────────────────────┐  ┌────────────────────────┐                  │
│  │ PollingBoothSerializer │  │ PollingBoothList       │                  │
│  │ (Full details)         │  │ Serializer (Minimal)   │                  │
│  └────────────────────────┘  └────────────────────────┘                  │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                         MODEL LAYER (Django ORM)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  PollingBooth Model                                                 │ │
│  │  ├── ForeignKey: State, District, Constituency                     │ │
│  │  ├── Fields: booth_number, name, building_name                     │ │
│  │  ├── Location: address, area, landmark, pincode                    │ │
│  │  ├── Coordinates: latitude, longitude                              │ │
│  │  ├── Stats: total_voters, male_voters, female_voters               │ │
│  │  └── Status: is_active, is_accessible                              │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬───────────────────────────────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────────────────┐
│                         DATABASE LAYER (PostgreSQL)                       │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │  Tables:                                                            │ │
│  │  ├── api_pollingbooth       (Main booth data)                      │ │
│  │  ├── api_state              (States reference)                     │ │
│  │  ├── api_district           (Districts reference)                  │ │
│  │  ├── api_constituency       (Constituencies reference)             │ │
│  │  ├── api_userprofile        (User roles & assignments)             │ │
│  │  └── Indexes on state, district, constituency, booth_number        │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

## Data Flow - Bulk Upload

```
┌──────────────┐
│   Client     │
│  Uploads CSV │
└──────┬───────┘
       │
       │ 1. POST /api/polling-booths/bulk-upload/
       │    Content-Type: multipart/form-data
       │    Authorization: Bearer <JWT_TOKEN>
       │
┌──────▼───────────────────────────────────────────────┐
│  Django URL Router                                   │
│  → political_urls.py                                 │
│  → PollingBoothViewSet.bulk_upload()                 │
└──────┬───────────────────────────────────────────────┘
       │
       │ 2. Permission Check
       │
┌──────▼───────────────────────────────────────────────┐
│  CanManagePollingBooths.has_permission()             │
│  → Verify user.profile.role in ['admin', 'superadmin']│
│  → ✓ Allowed / ✗ 403 Forbidden                       │
└──────┬───────────────────────────────────────────────┘
       │
       │ 3. File Validation
       │
┌──────▼───────────────────────────────────────────────┐
│  bulk_upload() method                                │
│  ├── Check file exists                               │
│  ├── Validate extension (.csv, .xlsx, .xls)          │
│  ├── Validate size (< 10 MB)                         │
│  └── Read file into pandas DataFrame                 │
└──────┬───────────────────────────────────────────────┘
       │
       │ 4. Data Validation
       │
┌──────▼───────────────────────────────────────────────┐
│  Column & Row Validation                             │
│  ├── Check required columns present                  │
│  ├── Check row count (1 to 10,000)                   │
│  └── Validate data types                             │
└──────┬───────────────────────────────────────────────┘
       │
       │ 5. Process Upload
       │
┌──────▼───────────────────────────────────────────────┐
│  _process_bulk_upload() method                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  1. Cache Reference Data                      │  │
│  │     state_cache = {code: State}              │  │
│  │     district_cache = {code: District}         │  │
│  │     constituency_cache = {code: Constituency} │  │
│  └────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────┐  │
│  │  2. For each row in DataFrame:               │  │
│  │     ├── Validate foreign keys (state, etc)   │  │
│  │     ├── Validate required fields             │  │
│  │     ├── Parse numeric/boolean values         │  │
│  │     ├── Check for existing booth             │  │
│  │     │   (constituency + booth_number)        │  │
│  │     ├── If exists: UPDATE                    │  │
│  │     ├── If new: CREATE                       │  │
│  │     └── Track success/errors                 │  │
│  └────────────────────────────────────────────────┘  │
└──────┬───────────────────────────────────────────────┘
       │
       │ 6. Database Operations
       │
┌──────▼───────────────────────────────────────────────┐
│  Django ORM → PostgreSQL                             │
│  ├── PollingBooth.objects.create(**data)             │
│  ├── existing_booth.save()                           │
│  └── Transactions maintain integrity                 │
└──────┬───────────────────────────────────────────────┘
       │
       │ 7. Response
       │
┌──────▼───────────────────────────────────────────────┐
│  Return JSON Response                                │
│  {                                                   │
│    "success": true,                                  │
│    "total_rows": 100,                                │
│    "success_count": 95,                              │
│    "failed_count": 5,                                │
│    "errors": [                                       │
│      {"row": 12, "error": "...", "data": {...}}     │
│    ]                                                 │
│  }                                                   │
└──────┬───────────────────────────────────────────────┘
       │
       │ 8. Client receives response
       │
┌──────▼───────────────────────────────────────────────┐
│  Client handles response                             │
│  ├── Show success message                            │
│  ├── Display error list                              │
│  └── Allow user to fix and re-upload failed rows     │
└──────────────────────────────────────────────────────┘
```

## Permission Flow

```
User Role: Admin (assigned_state = Tamil Nadu)

Request: GET /api/polling-booths/

Flow:
┌─────────────────────────────────────────────────────┐
│ 1. Authentication (JWT Token)                       │
│    → user.profile.role = 'admin'                    │
│    → user.profile.assigned_state = State('TN')      │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│ 2. Permission Check                                 │
│    → CanManagePollingBooths.has_permission()        │
│    → GET request: Allow (any authenticated user)    │
│    → ✓ Pass                                         │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│ 3. Data Isolation (get_queryset)                    │
│    → role = 'admin'                                 │
│    → Filter: queryset.filter(state=assigned_state)  │
│    → Result: Only booths in Tamil Nadu              │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│ 4. Serialization                                    │
│    → PollingBoothListSerializer (lightweight)       │
│    → Return: [booth1, booth2, ...]                  │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│ 5. Response                                         │
│    → Only Tamil Nadu booths returned                │
│    → Admin cannot see other states                  │
└─────────────────────────────────────────────────────┘
```

## Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  API Layer (DRF)                                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PollingBoothViewSet                                   │ │
│  │  ├── list()          → List booths (GET)              │ │
│  │  ├── retrieve()      → Get booth (GET)                │ │
│  │  ├── create()        → Create booth (POST)            │ │
│  │  ├── update()        → Update booth (PUT/PATCH)       │ │
│  │  ├── destroy()       → Delete booth (DELETE)          │ │
│  │  ├── bulk_upload()   → Upload CSV/Excel (POST)        │ │
│  │  ├── template()      → Download template (GET)        │ │
│  │  └── stats()         → Get statistics (GET)           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Permissions                                           │ │
│  │  └── CanManagePollingBooths                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Serializers                                           │ │
│  │  ├── PollingBoothSerializer (full)                    │ │
│  │  └── PollingBoothListSerializer (lightweight)         │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Business Logic Layer                                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  _process_bulk_upload()                                │ │
│  │  ├── Parse CSV/Excel (pandas)                          │ │
│  │  ├── Validate data                                     │ │
│  │  ├── Cache lookups                                     │ │
│  │  ├── Process rows                                      │ │
│  │  └── Return results                                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  get_queryset() - Data Isolation                       │ │
│  │  ├── Check user role                                   │ │
│  │  ├── Apply geographic filter                           │ │
│  │  └── Return filtered queryset                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Data Layer (Django ORM)                                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Models                                                │ │
│  │  ├── PollingBooth                                      │ │
│  │  ├── State                                             │ │
│  │  ├── District                                          │ │
│  │  ├── Constituency                                      │ │
│  │  └── UserProfile                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL)                                       │
│                                                              │
│  ├── api_pollingbooth                                       │
│  ├── api_state                                              │
│  ├── api_district                                           │
│  ├── api_constituency                                       │
│  └── api_userprofile                                        │
└──────────────────────────────────────────────────────────────┘
```

## Tech Stack

```
┌──────────────────────────────────────┐
│  Backend Framework                   │
│  Django 5.2 + Django REST Framework  │
└──────────────────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Authentication                      │
│  JWT (djangorestframework-simplejwt) │
└──────────────────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Data Processing                     │
│  pandas 2.2.0 (CSV/Excel)            │
│  openpyxl 3.1.2 (Excel support)      │
└──────────────────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│  Database                            │
│  PostgreSQL (production)             │
│  SQLite (development)                │
└──────────────────────────────────────┘
```

## File Structure

```
backend/
├── api/
│   ├── models.py                          # PollingBooth, State, etc.
│   ├── permissions/
│   │   └── role_permissions.py            # CanManagePollingBooths
│   ├── views/
│   │   └── polling_booths.py              # PollingBoothViewSet ★
│   ├── political_serializers.py           # Serializers
│   └── urls/
│       └── political_urls.py              # URL routing
├── docs/
│   ├── POLLING_BOOTH_BULK_UPLOAD.md       # Full API docs
│   └── ARCHITECTURE_DIAGRAM.md            # This file
├── tests/
│   └── test_polling_booth_upload.py       # Test suite
└── requirements.txt                        # Dependencies

Project Root/
├── POLLING_BOOTH_IMPLEMENTATION_SUMMARY.md  # Summary
└── QUICK_START_POLLING_BOOTH_API.md         # Quick reference
```

---

**Legend:**
- ★ = Main implementation file
- → = Data flow
- ├── = File/component structure
- ✓ = Success path
- ✗ = Error path
