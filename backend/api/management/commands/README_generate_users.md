# Generate Users Management Command

## Overview

The `generate_users` Django management command creates a complete user hierarchy for the Pulse of People platform with **640 users** featuring realistic Tamil names.

## Command Location

```
/Users/murali/Applications/pulseofpeople/backend/api/management/commands/generate_users.py
```

## Prerequisites

Before running this command, ensure the following data exists in your database:

1. **Political Data** (States, Districts, Constituencies)
   ```bash
   python manage.py seed_political_data
   ```

2. **Database Migrations** (up-to-date)
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

## Usage

### Basic Usage

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python manage.py generate_users
```

### With Options

```bash
# Skip creation if users already exist
python manage.py generate_users --skip-existing
```

## Generated User Hierarchy

The command creates **640 users** distributed across 7 roles:

| Role | Count | Description | Email Pattern | Password |
|------|-------|-------------|---------------|----------|
| **Superadmin** | 1 | Platform administrator | `superadmin@pulseofpeople.com` | `Admin@123` |
| **Admin** | 1 | TVK State Leader (Vijay) | `vijay@tvk.com` | `Vijay@2026` |
| **Manager** | 38 | District-level managers (one per TN district) | `manager.<district>@tvk.com` | `Manager@2024` |
| **Analyst** | 100 | Constituency-level analysts | `analyst.<constituency>@tvk.com` | `Analyst@2024` |
| **User** | 450 | Booth agents with ward/booth assignments | `user1@tvk.com` to `user450@tvk.com` | `User@2024` |
| **Volunteer** | 50 | Field workers without fixed assignments | `volunteer1@tvk.com` to `volunteer50@tvk.com` | `Volunteer@2024` |
| **TOTAL** | **640** | Complete user hierarchy | - | - |

## User Details

### 1. Superadmin (1 user)
- **Username**: `superadmin`
- **Email**: `superadmin@pulseofpeople.com`
- **Password**: `Admin@123`
- **Permissions**: Full platform access
- **Assignments**: None (system-wide access)

### 2. Admin (1 user - Vijay)
- **Username**: `vijay`
- **Email**: `vijay@tvk.com`
- **Password**: `Vijay@2026`
- **Role**: TVK Party Leader
- **Assigned State**: Tamil Nadu
- **Bio**: "TVK Party Leader - State Admin for Tamil Nadu"

### 3. Managers (38 users - one per district)
- **Email Pattern**: `manager.<district>@tvk.com`
  - Example: `manager.chennai@tvk.com`, `manager.coimbatore@tvk.com`
- **Password**: `Manager@2024`
- **Assignments**: Each manager is assigned to a specific district
- **Districts Covered**: All 38 Tamil Nadu districts
- **Names**: Realistic Tamil names using Faker library

**Sample Districts**:
- Ariyalur, Chengalpattu, Chennai, Coimbatore, Cuddalore
- Dharmapuri, Dindigul, Erode, Kallakurichi, Kanchipuram
- Kanyakumari, Karur, Krishnagiri, Madurai, Mayiladuthurai
- (... and 23 more)

### 4. Analysts (100 users - one per constituency)
- **Email Pattern**: `analyst.<constituency>@tvk.com`
  - Example: `analyst.gummidipoondi@tvk.com`, `analyst.chennai3@tvk.com`
- **Password**: `Analyst@2024`
- **Assignments**: Each analyst is assigned to a specific constituency
- **Constituencies**: Top 100 constituencies in Tamil Nadu
- **Names**: Realistic Tamil names

**Sample Constituencies**:
- Gummidipoondi, Ponneri, Tiruvottiyur, Radhakrishnan Nagar
- Perambur, Kolathur, Thiru-Vi-Ka-Nagar, Royapuram
- (... and 92 more)

### 5. Users/Booth Agents (450 users)
- **Email Pattern**: `user<number>@tvk.com` (user1 to user450)
  - Example: `user1@tvk.com`, `user250@tvk.com`
- **Password**: `User@2024`
- **Assignments**:
  - Ward-level assignments
  - Constituency assignments
  - BoothAgent profiles with 1-3 booth assignments each
- **Names**: Realistic Tamil names
- **Bio**: "Booth agent for {ward name}"

**BoothAgent Profile Details**:
- `assigned_wards`: Array of ward names (e.g., `['Anna Nagar']`)
- `assigned_booths`: Array of booth numbers (e.g., `['001', '002', '003']`)
- `constituency`: Linked to specific constituency
- `district`: Linked to district
- `state`: Tamil Nadu

### 6. Volunteers (50 users)
- **Email Pattern**: `volunteer<number>@tvk.com` (volunteer1 to volunteer50)
  - Example: `volunteer1@tvk.com`, `volunteer25@tvk.com`
- **Password**: `Volunteer@2024`
- **Assignments**: Random district assignments (no fixed wards/booths)
- **Names**: Realistic Tamil names
- **Bio**: "TVK volunteer and field worker"

## Generated Data Features

### Realistic Tamil Names
- **First Names**: Arun, Balaji, Chidambaram, Dinesh, Priya, Radha, Saranya, etc.
- **Last Names**: Kumar, Raj, Selvam, Murugan, Pillai, Naicker, Chettiar, etc.
- Uses Faker library with `en_IN` locale for authentic Indian names

### Phone Numbers
- **Format**: `+91XXXXXXXXXX` (Indian format)
- **Prefixes**: 90-99 (valid mobile prefixes)
- **Example**: `+919876543210`

### Timestamps
- **Created Dates**: Randomly distributed over last 6 months
- Adds realism to user account history

### Geographic Assignments
- **State**: Tamil Nadu
- **Districts**: All 38 districts covered
- **Constituencies**: 100 constituencies
- **Wards**: 25+ ward names (repeated across constituencies)

## Database Impact

### Tables Populated
1. `auth_user` - Django User model (640 records)
2. `api_userprofile` - Extended user profiles (640 records)
3. `api_boothagent` - Booth agent profiles (450 records)

### Organization
- All users are assigned to **Tamilaga Vettri Kazhagam (TVK)** organization
- Organization slug: `tvk`

## Sample Login Credentials

### Platform Access
```
Superadmin:
  Email:    superadmin@pulseofpeople.com
  Password: Admin@123
```

### TVK Leadership
```
Admin (Vijay):
  Email:    vijay@tvk.com
  Password: Vijay@2026
```

### District Management
```
Managers (any district):
  Email:    manager.<district>@tvk.com
  Password: Manager@2024
  Example:  manager.chennai@tvk.com
```

### Constituency Analysis
```
Analysts (any constituency):
  Email:    analyst.<constituency>@tvk.com
  Password: Analyst@2024
  Example:  analyst.gummidipoondi@tvk.com
```

### Booth Operations
```
Users/Booth Agents:
  Email:    user1@tvk.com to user450@tvk.com
  Password: User@2024
```

### Field Operations
```
Volunteers:
  Email:    volunteer1@tvk.com to volunteer50@tvk.com
  Password: Volunteer@2024
```

## Command Output

The command provides detailed progress tracking:

```
======================================================================
GENERATING USER HIERARCHY FOR PULSE OF PEOPLE
======================================================================

[1/7] Setting up organization and geography data...
  Created TVK organization
  Loaded state: Tamil Nadu
  Loaded 38 districts
  Loaded 100 constituencies
  Generated 500 ward assignments

[2/7] Creating Superadmin (1 user)...
  Created: superadmin (superadmin@pulseofpeople.com)

[3/7] Creating Admin (1 user)...
  Created: vijay (vijay@tvk.com)

[4/7] Creating Managers (38 users - one per district)...
  [1/38] Ariyalur: manager.ariyalur
  ...
  Created 38 managers

[5/7] Creating Analysts (100 users - one per constituency)...
  ...
  Created 100 analysts

[6/7] Creating Users/Booth Agents (450 users)...
  ...
  Created 450 users/booth agents

[7/7] Creating Volunteers (50 users)...
  ...
  Created 50 volunteers

======================================================================
SUMMARY
======================================================================

Organization: Tamilaga Vettri Kazhagam
State: Tamil Nadu

Users by Role:
  Superadmin:    1 users
  Admin:         1 users
  Manager:      38 users (one per district)
  Analyst:     100 users (one per constituency)
  User:        450 users (booth agents)
  Volunteer:    50 users
  ――――――――――――――――――――――――――――――――――――――――――――――――――
  TOTAL:       640 users

Booth Agent Profiles: 450
```

## Verification

After running the command, verify the data:

```bash
python manage.py shell
```

```python
from api.models import User, UserProfile, Organization, BoothAgent

org = Organization.objects.get(slug='tvk')
print(f'Total Users: {User.objects.count()}')
print(f'Users in TVK: {UserProfile.objects.filter(organization=org).count()}')
print(f'Booth Agents: {BoothAgent.objects.count()}')

# Check specific role counts
for role, name in UserProfile.ROLE_CHOICES:
    count = UserProfile.objects.filter(role=role, organization=org).count()
    print(f'{name}: {count}')
```

Expected output:
```
Total Users: 640
Users in TVK: 640
Booth Agents: 450
Super Admin: 1
Admin: 1
Manager: 38
Analyst: 100
User: 450
Viewer: 0
Volunteer: 50
```

## Re-running the Command

The command is **idempotent** - it uses `get_or_create()` for users and always updates profiles. This means:

- Running it multiple times will **update** existing users rather than create duplicates
- Safe to re-run after code changes
- User passwords will NOT be reset on re-run (unless user was newly created)

## Troubleshooting

### Error: "Tamil Nadu state not found"
**Solution**: Run `python manage.py seed_political_data` first

### Error: "no such table: api_twofactorbackupcode"
**Solution**: Run migrations with `python manage.py migrate`

### Error: "Only X constituencies available"
**Solution**: Create more constituencies using the shell or import_electoral_data command

### Slow performance
- Command creates 640 users with phone numbers and timestamps
- Expected runtime: 30-60 seconds
- Uses Django transactions for data integrity

## Technical Details

### Dependencies
- **Django**: User and authentication system
- **Faker**: Realistic Tamil names (en_IN locale)
- **api.models**: UserProfile, Organization, State, District, Constituency, BoothAgent

### Database Transactions
- All user creation happens within a single transaction
- Rollback on any error to maintain data integrity

### Performance Optimizations
- Uses `get_or_create()` to prevent duplicates
- Batch processing for booth agents
- Progress tracking every N users to reduce output

## Use Cases

1. **Development Testing**: Populate dev database with realistic user data
2. **Demo Environment**: Show complete TVK organizational structure
3. **Permission Testing**: Test role-based access control across all 7 roles
4. **UI Testing**: Verify dashboards with different role views
5. **Data Analysis**: Test analytics with multi-level hierarchy
6. **API Testing**: Test user management endpoints with real data

## Next Steps

After generating users:

1. **Test Login**: Try logging in with different roles
2. **Test Permissions**: Verify each role's access levels
3. **Seed Additional Data**: Run other seed commands for voters, feedback, etc.
4. **Configure Frontend**: Update frontend to recognize these roles
5. **Test Workflows**: Create campaigns, assign tasks, collect feedback

## Related Commands

```bash
# Seed political data (prerequisite)
python manage.py seed_political_data

# Seed permissions and role mappings
python manage.py seed_permissions

# Seed polling booth data
python manage.py seed_polling_booths

# Seed voter data
python manage.py seed_voters

# Seed complete dataset
python manage.py seed_all_data
```

## Notes

- All passwords are for **development use only**
- Change passwords for production deployment
- Phone numbers are randomly generated (not real)
- Tamil names are randomly generated using Faker
- Geographic data (districts, constituencies) must exist before running
- Organization "Tamilaga Vettri Kazhagam" (TVK) is auto-created if missing

## Author

Generated for Pulse of People Platform - TVK Edition

## Last Updated

2025-11-09
