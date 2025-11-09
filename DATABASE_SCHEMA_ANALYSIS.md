# Pulse of People - Database Schema Analysis

## Executive Summary
The Pulse of People platform uses Django ORM with a comprehensive schema supporting political sentiment analysis, voter management, campaign tracking, and multi-tenant operations. The database has **40+ core tables** organized into 5 functional domains.

**Database Engine**: PostgreSQL (production) / SQLite (development)
**Migration Status**: 10 active migrations with schema fully defined in models.py and models_analytics.py

---

## I. AUTHENTICATION & USER MANAGEMENT TABLES

### 1. **auth_user** (Django built-in)
- **Purpose**: Core user authentication
- **Columns**:
  - id (PK, int)
  - username (unique)
  - email (indexed)
  - password (hashed)
  - first_name, last_name
  - is_active, is_staff, is_superuser
  - date_joined, last_login

### 2. **api_userprofile** 
- **Purpose**: Extended user profile with roles and location assignments
- **Key Columns**:
  - id (PK)
  - user_id (FK → auth_user, OneToOne)
  - role (superadmin|admin|manager|analyst|user|viewer|volunteer)
  - organization_id (FK → Organization)
  - avatar, avatar_url, bio, phone, date_of_birth
  - **Location Assignments** (hierarchical):
    - assigned_state_id (FK → State) - Admin1 level
    - assigned_district_id (FK → District) - Admin2 level
    - city, constituency (free text for Admin3)
  - **2FA Fields**:
    - is_2fa_enabled (boolean)
    - totp_secret (char(32))
    - must_change_password (boolean)
  - custom_permissions (M2M → Permission via UserPermission)
  - created_at, updated_at

**Key Indexes**:
  - (user_id) - OneToOne lookup
  - (organization_id, role) - Org member queries

### 3. **api_permission**
- **Purpose**: Granular permission definitions (67 total)
- **Columns**:
  - id (PK)
  - name (unique, max 100)
  - category (users|data|analytics|settings|system)
  - description
  - created_at

### 4. **api_rolepermission**
- **Purpose**: Maps roles to permissions (role-based access control)
- **Columns**:
  - id (PK)
  - role (CharField - superadmin|admin|manager|analyst|user|viewer|volunteer)
  - permission_id (FK → Permission)
- **Constraints**: unique_together(role, permission_id)

### 5. **api_userpermission**
- **Purpose**: User-specific permission overrides
- **Columns**:
  - id (PK)
  - user_profile_id (FK → UserProfile)
  - permission_id (FK → Permission)
  - granted (boolean) - can revoke permissions
  - created_at
- **Constraints**: unique_together(user_profile_id, permission_id)

### 6. **api_organization**
- **Purpose**: Multi-tenancy support (political parties, campaigns, NGOs)
- **Columns**:
  - id (PK)
  - name (max 200)
  - slug (unique)
  - organization_type (party|campaign|ngo|other)
  - **Contact**: contact_email, contact_phone, address, city, state
  - website, social_media_links (JSON)
  - **Subscription**:
    - subscription_plan (free|basic|pro|enterprise)
    - subscription_status, subscription_expires_at
    - max_users
  - logo (ImageField)
  - settings (JSON - branding, email templates, etc.)
  - is_active
  - created_at, updated_at

**Relationships**:
  - members (reverse from UserProfile)

### 7. **api_twoFactorBackupCode**
- **Purpose**: 2FA recovery backup codes
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user)
  - code_hash (char 255)
  - is_used
  - used_at
  - created_at
- **Index**: (user_id, is_used)

---

## II. GEOGRAPHIC/POLITICAL HIERARCHY TABLES

### 8. **api_state**
- **Purpose**: Indian states (top-level geographic division)
- **Columns**:
  - id (PK)
  - name (unique, max 100)
  - code (unique, max 10)
  - capital
  - region
  - total_districts (int, denormalized for speed)
  - total_constituencies (int, denormalized)
  - created_at, updated_at

### 9. **api_district**
- **Purpose**: Districts within states
- **Columns**:
  - id (PK)
  - state_id (FK → State) - required
  - name (max 100)
  - code (unique, max 20)
  - headquarters
  - population (int, nullable)
  - area_sq_km (decimal 10,2)
  - total_wards (int)
  - created_at, updated_at
- **Constraints**: unique_together(state_id, name)
- **Indexes**:
  - (state_id, name)
  - (code)

### 10. **api_constituency**
- **Purpose**: Electoral constituencies (both Assembly & Parliamentary)
- **Columns**:
  - id (PK)
  - state_id (FK → State) - required
  - district_id (FK → District, nullable)
  - name (max 200)
  - code (unique, max 20)
  - constituency_type (assembly|parliamentary)
  - number (int) - official constituency number
  - reserved_for (general|sc|st)
  - total_voters (int)
  - total_wards (int)
  - total_booths (int)
  - area_sq_km (decimal)
  - **Geographic Center**:
    - center_lat (decimal 10,8)
    - center_lng (decimal 11,8)
  - geojson_data (JSON) - boundary for Mapbox
  - metadata (JSON)
  - created_at, updated_at
- **Constraints**: unique_together(state_id, code)
- **Indexes**:
  - (state_id, constituency_type)
  - (code)
  - (district_id)

### 11. **api_pollingbooth**
- **Purpose**: Voting stations within constituencies
- **Columns**:
  - id (PK)
  - state_id, district_id, constituency_id (FKs - all required)
  - booth_number (max 20) - e.g., '001', '002A'
  - name (max 300)
  - building_name (max 200)
  - **Location Details**:
    - address
    - area (locality name)
    - landmark
    - pincode (10 chars)
  - **Coordinates**:
    - latitude (decimal 10,8), longitude (decimal 11,8)
  - **Voter Statistics**:
    - total_voters (int)
    - male_voters, female_voters, other_voters
  - **Status**:
    - is_active (boolean)
    - is_accessible (wheelchair) (boolean)
  - metadata (JSON)
  - created_at, updated_at
- **Constraints**: unique_together(constituency_id, booth_number)
- **Indexes**:
  - (state_id, district_id)
  - (constituency_id)
  - (booth_number)
  - (is_active)

---

## III. VOTER & ENGAGEMENT TABLES

### 12. **api_voter**
- **Purpose**: Core voter database with sentiment tracking
- **Columns**:
  - id (PK)
  - voter_id (unique, char 50, indexed) - official voter ID
  - **Identity**:
    - first_name (max 100)
    - last_name (max 100)
    - middle_name (max 100)
    - date_of_birth
    - age (int 18-120)
    - gender (male|female|other)
    - photo (ImageField)
  - **Contact**:
    - phone (max 20, indexed)
    - alternate_phone
    - email
  - **Address**:
    - address_line1, address_line2 (max 200)
    - landmark
    - ward (max 100, indexed)
    - pincode
  - **Geographic Relationships**:
    - constituency_id (FK → Constituency)
    - district_id (FK → District)
    - state_id (FK → State)
    - latitude, longitude (decimal)
  - **Political Data**:
    - party_affiliation (bjp|congress|aap|tvk|dmk|aiadmk|neutral|unknown|other)
    - voting_history (JSON - last 5 elections)
    - sentiment (strong_supporter|supporter|neutral|opposition|strong_opposition)
    - influence_level (high|medium|low)
    - is_opinion_leader (boolean)
  - **Engagement Tracking**:
    - last_contacted_at (datetime)
    - contact_frequency (int)
    - interaction_count (int)
    - positive_interactions (int)
    - negative_interactions (int)
    - preferred_communication (phone|sms|whatsapp|email|door_to_door)
  - **Metadata**:
    - created_by_id (FK → auth_user)
    - is_active, is_verified
    - tags (JSON)
    - notes
    - created_at, updated_at
- **Indexes**:
  - (voter_id)
  - (constituency_id, ward)
  - (party_affiliation)
  - (sentiment)
  - (phone)
  - (is_active)
  - (-created_at)

### 13. **api_voterinteraction**
- **Purpose**: Track all interactions with voters
- **Columns**:
  - id (PK)
  - voter_id (FK → Voter)
  - interaction_type (phone_call|door_visit|event_meeting|sms|email|whatsapp)
  - contacted_by_id (FK → auth_user)
  - interaction_date (datetime, auto_now_add)
  - duration_minutes (int, nullable)
  - sentiment (positive|neutral|negative)
  - issues_discussed (JSON)
  - promises_made (text)
  - follow_up_required (boolean)
  - follow_up_date
  - notes
  - created_at
- **Indexes**:
  - (voter_id, -interaction_date)
  - (contacted_by_id)
  - (interaction_type)
  - (sentiment)
  - (follow_up_required)

### 14. **api_boothagent**
- **Purpose**: Extended profile for Admin3 (booth-level party workers)
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user, OneToOne)
  - state_id, district_id, constituency_id (FKs)
  - assigned_wards (JSON array)
  - assigned_booths (JSON array)
  - focus_segments (M2M → VoterSegment)
  - total_reports (int)
  - total_feedback_collected (int)
  - last_report_date
  - phone
  - is_active
  - joined_date
  - created_at, updated_at
- **Indexes**:
  - (constituency_id)
  - (district_id)
  - (is_active)

### 15. **api_volunteerprofile**
- **Purpose**: Extended volunteer profile with skills tracking
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user, OneToOne)
  - volunteer_id (unique, max 50, indexed)
  - skills (JSON array)
  - availability (JSON dict - days/times)
  - assigned_ward (max 100)
  - assigned_constituency_id (FK → Constituency)
  - tasks_completed (int)
  - hours_contributed (decimal 10,2)
  - rating (decimal 3,2 - 0 to 5)
  - is_active
  - joined_at
  - created_at, updated_at
- **Indexes**:
  - (volunteer_id)
  - (assigned_constituency_id)
  - (is_active)

---

## IV. FEEDBACK & REPORTING TABLES

### 16. **api_directfeedback**
- **Purpose**: Direct citizen feedback submissions with AI analysis
- **Columns**:
  - id (PK)
  - feedback_id (UUID, unique)
  - **Citizen Data**:
    - citizen_name (max 200)
    - citizen_age (18-120)
    - citizen_phone, citizen_email
  - **Location**:
    - state_id, district_id, constituency_id (FKs, nullable)
    - ward (max 100)
    - booth_number (max 20)
    - detailed_location (text)
  - **Feedback Content**:
    - issue_category_id (FK → IssueCategory)
    - message_text
    - expectations
    - voter_segment_id (FK → VoterSegment)
  - **Media**:
    - audio_file_url, video_file_url, image_urls (JSON)
    - transcription (text)
  - **AI Analysis**:
    - ai_summary
    - ai_sentiment_score (decimal 4,2 0-1)
    - ai_sentiment_polarity (positive|negative|neutral)
    - ai_extracted_issues (JSON)
    - ai_urgency (low|medium|high|urgent)
    - ai_confidence (decimal 4,2 0-1)
    - ai_analysis_metadata (JSON)
  - **Workflow**:
    - status (pending|analyzing|analyzed|reviewed|escalated|resolved)
    - assigned_to_id (FK → auth_user)
    - reviewed_by_id (FK → auth_user)
    - review_notes
  - **Timestamps**:
    - submitted_at, analyzed_at, reviewed_at
    - created_at, updated_at
    - supabase_id (UUID sync)
- **Indexes**:
  - (status)
  - (ward)
  - (constituency_id)
  - (-submitted_at)
  - (assigned_to_id)
  - (issue_category_id)
  - (voter_segment_id)

### 17. **api_fieldreport**
- **Purpose**: Ground-level reports from party workers/volunteers
- **Columns**:
  - id (PK)
  - report_id (UUID, unique)
  - volunteer_id (FK → auth_user)
  - state_id, district_id, constituency_id (FKs)
  - ward, booth_number
  - **Location**:
    - location_lat, location_lng (decimals)
    - address
  - **Report Content**:
    - report_type (daily_summary|event_feedback|issue_report|competitor_activity|booth_report)
    - title
    - positive_reactions (JSON)
    - negative_reactions (JSON)
    - key_issues (M2M → IssueCategory)
    - voter_segments_met (M2M → VoterSegment)
    - crowd_size (int)
    - quotes (JSON)
    - notes
    - competitor_party_id (FK → PoliticalParty, nullable)
    - competitor_activity_description
    - media_urls (JSON)
  - **Verification**:
    - verification_status (pending|verified|disputed)
    - verified_by_id (FK → auth_user)
    - verified_at, verification_notes
  - **Timestamps**:
    - report_date, timestamp, created_at, updated_at
    - supabase_id (UUID sync)
- **Indexes**:
  - (volunteer_id, -timestamp)
  - (ward)
  - (booth_number)
  - (constituency_id)
  - (verification_status)
  - (report_type)
  - (-timestamp)
  - (report_date)

### 18. **api_sentimentdata**
- **Purpose**: Aggregated sentiment analysis data from multiple sources
- **Columns**:
  - id (PK)
  - source_type (direct_feedback|field_report|social_media|survey)
  - source_id (UUID)
  - issue_id (FK → IssueCategory)
  - sentiment_score (decimal 4,2 0-1)
  - polarity (positive|negative|neutral)
  - confidence (decimal 4,2 0-1)
  - **Geographic**:
    - state_id, district_id, constituency_id (FKs, nullable)
    - ward (max 100)
  - voter_segment_id (FK → VoterSegment, nullable)
  - timestamp, created_at
  - supabase_id (UUID sync)
- **Indexes**:
  - (issue_id, -timestamp)
  - (polarity)
  - (constituency_id, -timestamp)
  - (district_id, -timestamp)
  - (ward)
  - (-timestamp)
  - (voter_segment_id)

---

## V. CAMPAIGN & EVENT TABLES

### 19. **api_campaign**
- **Purpose**: Campaign management (elections, awareness, door-to-door)
- **Columns**:
  - id (PK)
  - campaign_name (max 200)
  - campaign_type (election|awareness|issue_based|door_to_door)
  - start_date, end_date
  - status (planning|active|completed|cancelled)
  - budget, spent_amount (decimal 12,2)
  - target_constituency_id (FK → Constituency, nullable)
  - target_audience (text)
  - campaign_manager_id (FK → auth_user)
  - team_members (M2M → auth_user)
  - goals, metrics (JSON)
  - created_by_id (FK → auth_user)
  - created_at, updated_at
- **Indexes**:
  - (status)
  - (campaign_type)
  - (start_date)
  - (campaign_manager_id)

### 20. **api_event**
- **Purpose**: Event management (rallies, meetings, door-to-door events)
- **Columns**:
  - id (PK)
  - event_name (max 200)
  - event_type (rally|meeting|door_to_door|booth_visit|town_hall)
  - start_datetime, end_datetime
  - location (max 300)
  - ward (max 100)
  - constituency_id (FK → Constituency, nullable)
  - **Coordinates**:
    - latitude, longitude (decimals)
  - **Attendance**:
    - expected_attendance, actual_attendance (ints)
  - **Team**:
    - organizer_id (FK → auth_user)
    - volunteers (M2M → auth_user)
  - campaign_id (FK → Campaign, nullable)
  - **Budget**:
    - budget, expenses (decimal 10,2)
  - status (planned|ongoing|completed|cancelled)
  - notes
  - photos (JSON - URLs)
  - created_at, updated_at
- **Indexes**:
  - (event_type)
  - (status)
  - (start_datetime)
  - (constituency_id)

### 21. **api_socialmediapost**
- **Purpose**: Social media post tracking and engagement metrics
- **Columns**:
  - id (PK)
  - platform (facebook|twitter|instagram|whatsapp|youtube)
  - post_content (text)
  - post_url
  - post_id (max 200, platform-specific)
  - posted_at (datetime)
  - scheduled_at (datetime, nullable)
  - **Metrics**:
    - reach, impressions (ints)
    - engagement_count, likes, shares, comments_count
  - sentiment_score (decimal 4,2 0-1, nullable)
  - campaign_id (FK → Campaign, nullable)
  - posted_by_id (FK → auth_user)
  - is_published, is_promoted (booleans)
  - hashtags, mentions (JSON)
  - created_at, updated_at
- **Indexes**:
  - (platform, -posted_at)
  - (campaign_id)
  - (is_published)
  - (-posted_at)

---

## VI. ADMINISTRATIVE TABLES

### 22. **api_issuecategory**
- **Purpose**: Issue categories based on TVK priorities (hierarchical)
- **Columns**:
  - id (PK)
  - name (unique, max 100)
  - description
  - parent_id (FK → self, nullable) - for subcategories
  - color (hex, default #3B82F6)
  - icon (max 50)
  - priority (int)
  - is_active
  - created_at, updated_at

### 23. **api_votersegment**
- **Purpose**: Voter segments (Fishermen, Farmers, Youth, etc.)
- **Columns**:
  - id (PK)
  - name (unique, max 100)
  - description
  - estimated_population (int)
  - priority_level (int)
  - key_issues (M2M → IssueCategory)
  - is_active
  - created_at, updated_at

### 24. **api_politicalparty**
- **Purpose**: Political parties database
- **Columns**:
  - id (PK)
  - name (unique, max 200)
  - short_name (max 50)
  - symbol (max 100)
  - symbol_image (URL)
  - status (national|state|regional)
  - headquarters
  - website
  - founded_date
  - active_states (M2M → State)
  - ideology
  - description
  - created_at, updated_at

### 25. **api_expense**
- **Purpose**: Expense tracking for campaigns and events
- **Columns**:
  - id (PK)
  - expense_type (travel|materials|advertising|event|salary|other)
  - amount (decimal 10,2)
  - currency (default 'INR')
  - description
  - campaign_id (FK → Campaign, nullable)
  - event_id (FK → Event, nullable)
  - receipt_image (ImageField)
  - **Approval Workflow**:
    - approved_by_id (FK → auth_user)
    - status (pending|approved|rejected|paid)
  - paid_at
  - created_by_id (FK → auth_user)
  - created_at, updated_at
- **Indexes**:
  - (expense_type)
  - (status)
  - (campaign_id)
  - (event_id)
  - (-created_at)

### 26. **api_alert**
- **Purpose**: Alert/notification system for critical updates
- **Columns**:
  - id (PK)
  - alert_type (info|warning|urgent|critical)
  - title (max 200)
  - message (text)
  - target_role (max 20, or blank for all)
  - target_users (M2M → auth_user)
  - constituency_id, district_id (FKs, nullable)
  - priority (low|medium|high|urgent)
  - is_read, read_at (datetime)
  - expires_at
  - action_url, action_required
  - created_by_id (FK → auth_user)
  - created_at
- **Indexes**:
  - (target_role)
  - (priority)
  - (is_read)
  - (-created_at)

### 27. **api_notification**
- **Purpose**: User notifications synced with Supabase for real-time delivery
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user)
  - title (max 200)
  - message (text)
  - notification_type (info|success|warning|error|task|user|system)
  - is_read, read_at
  - related_model, related_id (for linking to entities)
  - metadata (JSON)
  - supabase_id (UUID, unique)
  - synced_to_supabase
  - created_at, updated_at
- **Indexes**:
  - (user_id, -created_at)
  - (is_read)
  - (notification_type)

### 28. **api_auditlog**
- **Purpose**: Audit log for tracking all user actions (GDPR/compliance)
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user, nullable)
  - action (create|read|update|delete|login|logout|permission_change|role_change)
  - target_model, target_id (max 100)
  - changes (JSON)
  - ip_address
  - user_agent
  - timestamp (auto_now_add)
- **Indexes**:
  - (user_id, timestamp)
  - (action)
  - (target_model, target_id)

### 29. **api_uploadedfile**
- **Purpose**: File metadata for uploads stored in Supabase Storage
- **Columns**:
  - id (PK)
  - user_id (FK → auth_user)
  - filename (max 255)
  - original_filename (max 255)
  - file_size (BigInt - bytes)
  - mime_type (max 100)
  - storage_path (max 500)
  - storage_url (max 500) - Supabase public URL
  - bucket_id (default 'user-files')
  - file_category (document|image|video|audio|archive|other)
  - metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (user_id, -created_at)
  - (file_category)
  - (mime_type)

---

## VII. BULK IMPORT TABLES

### 30. **api_bulkuploadjob**
- **Purpose**: Track bulk user upload jobs
- **Columns**:
  - id (PK)
  - job_id (UUID, unique)
  - created_by_id (FK → auth_user)
  - file_name (max 255)
  - file_path (max 500)
  - status (pending|validating|processing|completed|failed|cancelled)
  - total_rows, processed_rows, success_count, failed_count (ints)
  - validation_errors (JSON)
  - started_at, completed_at
  - created_at, updated_at
- **Indexes**:
  - (created_by_id, -created_at)
  - (status)
  - (job_id)

### 31. **api_bulkuploaderror**
- **Purpose**: Track errors for individual rows in bulk upload
- **Columns**:
  - id (PK)
  - job_id (FK → BulkUploadJob)
  - row_number (int)
  - row_data (JSON)
  - error_message (text)
  - error_field (max 100)
  - created_at
- **Indexes**:
  - (job_id, row_number)

---

## VIII. ANALYTICS AGGREGATION TABLES

### 32. **api_dailyvoterstats**
- **Purpose**: Aggregated daily voter statistics for faster analytics queries
- **Columns**:
  - id (PK)
  - date (DateField)
  - state_id, district_id, constituency_id (FKs, nullable)
  - **Totals**:
    - total_voters, new_voters (ints)
  - **Sentiment Breakdown**:
    - strong_supporters, supporters, neutral, opposition, strong_opposition (ints)
  - **Demographics**:
    - male_voters, female_voters, other_voters
  - **Age Groups**:
    - age_18_25, age_26_35, age_36_45, age_46_60, age_60_plus
  - metadata (JSON)
  - created_at, updated_at
- **Constraints**: unique_together(date, state_id, district_id, constituency_id)
- **Indexes**:
  - (date, state_id)
  - (date, district_id)
  - (date, constituency_id)
  - (-date)

### 33. **api_dailyinteractionstats**
- **Purpose**: Aggregated daily interaction statistics
- **Columns**:
  - id (PK)
  - date (DateField)
  - state_id, district_id, constituency_id (FKs, nullable)
  - **Interaction Counts**:
    - total_interactions, phone_calls, door_to_door, events, social_media
  - **Outcomes**:
    - conversions (neutral → supporter)
    - response_rate (decimal 5,2)
  - **Team Performance**:
    - active_volunteers, top_volunteer_id, top_volunteer_count
  - metadata (JSON)
  - created_at, updated_at
- **Constraints**: unique_together(date, state_id, district_id, constituency_id)
- **Indexes**:
  - (date, state_id)
  - (date, district_id)
  - (date, constituency_id)
  - (-date)

### 34. **api_dailysentimentstats**
- **Purpose**: Aggregated daily sentiment statistics
- **Columns**:
  - id (PK)
  - date (DateField)
  - state_id, district_id, constituency_id (FKs, nullable)
  - issue_id (FK → IssueCategory, nullable)
  - **Sentiment Metrics**:
    - avg_sentiment_score, sentiment_velocity (decimals)
    - positive_count, negative_count, neutral_count
  - **Source Breakdown**:
    - from_feedback, from_field_reports, from_social_media, from_surveys
  - metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (date, state_id)
  - (date, issue_id)
  - (date, constituency_id)
  - (-date)

### 35. **api_weeklycampaignstats**
- **Purpose**: Aggregated weekly campaign statistics
- **Columns**:
  - id (PK)
  - week_start, week_end (DateFields)
  - state_id, district_id (FKs, nullable)
  - **Campaign Metrics**:
    - total_campaigns, active_campaigns, completed_campaigns
  - **Performance**:
    - total_reach, total_budget, total_spent (decimals)
    - avg_roi (decimal 5,2)
  - **Engagement**:
    - total_interactions, total_conversions
  - metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (week_start, state_id)
  - (week_start, district_id)
  - (-week_start)

---

## IX. REPORTING TABLES

### 36. **api_reporttemplate**
- **Purpose**: Saved report templates for custom reports
- **Columns**:
  - id (PK)
  - template_id (UUID, unique)
  - name (max 200)
  - report_type (executive_summary|campaign_performance|constituency|daily_activity|weekly_summary|volunteer_performance|custom)
  - description
  - created_by_id (FK → auth_user)
  - **Configuration**:
    - metrics (JSON)
    - filters (JSON)
    - visualizations (JSON)
  - **Scheduling**:
    - is_scheduled
    - schedule_frequency (daily|weekly|monthly)
    - schedule_time, schedule_day
  - recipients (JSON - email addresses)
  - export_format (pdf|excel|both)
  - is_active
  - last_generated
  - metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (created_by_id, -created_at)
  - (report_type)
  - (is_scheduled)

### 37. **api_generatedreport**
- **Purpose**: Track generated reports
- **Columns**:
  - id (PK)
  - report_id (UUID, unique)
  - template_id (FK → ReportTemplate, nullable)
  - report_name (max 200)
  - report_type (max 50)
  - generated_by_id (FK → auth_user)
  - status (pending|generating|completed|failed)
  - **Files**:
    - pdf_file_url, excel_file_url (max 500)
    - file_size (BigInt)
    - generation_time (decimal 8,2 seconds)
  - **Access Control**:
    - download_count, expires_at
  - error_message
  - filters_used, metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (generated_by_id, -created_at)
  - (status)
  - (expires_at)
  - (-created_at)

### 38. **api_exportjob**
- **Purpose**: Track data export jobs (CSV, Excel, JSON, PDF)
- **Columns**:
  - id (PK)
  - job_id (UUID, unique)
  - created_by_id (FK → auth_user)
  - resource (max 50) - voters, interactions, etc.
  - export_format (csv|excel|json|pdf)
  - filters (JSON)
  - fields (JSON)
  - status (pending|processing|completed|failed)
  - progress (0-100)
  - **File Details**:
    - file_url (max 500)
    - file_size (BigInt)
    - row_count
  - **Timing**:
    - started_at, completed_at, expires_at
  - error_message
  - metadata (JSON)
  - created_at, updated_at
- **Indexes**:
  - (created_by_id, -created_at)
  - (status)
  - (job_id)

---

## X. DJANGO BUILT-IN TABLES (Reference)

### 39. **django_session**
- Session data for authenticated users

### 40. **django_migrations**
- Track applied migrations

### 41. **django_admin_log**
- Django admin action logs

### 42-45. **Django Auth Tables**
- auth_group, auth_group_permissions, auth_user_groups, auth_user_user_permissions

### 46-50. **Django Content Types**
- django_content_type (for generic relations)

---

## SCHEMA RELATIONSHIPS DIAGRAM

### Hierarchical Geographic Structure:
```
State
  ├── District (FK → State)
  │   ├── Constituency (FK → State, FK → District)
  │   │   └── PollingBooth (FK → State, District, Constituency)
  │   └── Voter (FK → State, District, Constituency)
  └── [Political/Admin relationships]
```

### User Access Control Hierarchy:
```
User (auth_user)
  ├── UserProfile (OneToOne)
  │   ├── Organization (FK)
  │   ├── RolePermission (FK, Role)
  │   └── UserPermission (M2M → Permission)
  ├── BoothAgent (OneToOne) [if Admin3]
  └── VolunteerProfile (OneToOne) [if Volunteer]
```

### Feedback & Analysis Pipeline:
```
DirectFeedback/FieldReport
  ├── IssueCategory (FK)
  ├── VoterSegment (FK)
  └── SentimentData (created from)
      └── DailySentimentStats (aggregated)
```

### Campaign & Engagement:
```
Campaign
  ├── Event (FK)
  ├── SocialMediaPost (FK)
  ├── TeamMembers (M2M → User)
  └── Voter [interactions via VoterInteraction]
```

---

## KEY STATISTICS

**Total Tables**: 50+ (including Django built-ins)
**Custom Tables**: 38
**Foreign Keys**: 80+
**Many-to-Many Relations**: 15+
**Indexed Columns**: 100+
**Unique Constraints**: 25+

**Largest Tables** (by typical volume):
1. Voter (millions in full deployment)
2. VoterInteraction (millions)
3. DirectFeedback (millions)
4. SentimentData (millions)
5. AuditLog (millions)
6. FieldReport (hundreds of thousands)

---

## MIGRATION HISTORY

```
0001_initial                               - Task, UserProfile
0002_userprofile_role                      - Add role field
0003_organization_permission_*             - Org, permissions, extended UserProfile
0004_notification                          - Notification model
0005_uploadedfile                          - File uploads for Supabase
0006_district_state_constituency_*         - Geographic hierarchy (30KB migration)
0007_userprofile_must_change_*             - 2FA, BulkUploadJob, errors, backup codes
0007_workstream2_core_models               - Voter, Campaign, Event, interactions (25KB migration)
0008_userprofile_city_constituency         - Add free-text location fields
0009_pollingbooth                          - Polling booth model
0010_merge_20251109_0533                   - Merge conflict resolution
```

---

## IMPORTANT NOTES FOR DATA GENERATION

### 1. **Hierarchical Constraints**
- All booths MUST have valid (state, district, constituency) references
- Voter state/district/constituency should match their ward location
- Consistency is critical for geographic filtering

### 2. **Index Coverage**
- Most frequent queries will use indexes on:
  - (constituency_id, ward) for booth/voter lookups
  - (-timestamp) for recent data retrieval
  - (is_active) for status filtering
  - (status) for workflow queries

### 3. **Multi-Tenant Isolation**
- Users filtered by organization_id
- Permissions checked via role + UserPermission

### 4. **Sentiment Score Normalization**
- All sentiment scores are 0.0-1.0 decimal
- Polarity is categorical (positive|negative|neutral)
- Confidence should correlate with sentiment analysis

### 5. **Geographic Data Precision**
- Latitude/Longitude use 8 decimal places (11m precision)
- State/District/Constituency codes are unique identifiers
- Ward names are free-text but should be consistent within constituency

### 6. **Audit Trail**
- Every significant action should create AuditLog entry
- Changes JSON captures before/after state
- IP address and user agent tracked

