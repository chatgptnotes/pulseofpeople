-- =====================================================
-- CONSTITUENCY ISSUES TABLE
-- For citizen-reported local issues
-- =====================================================

CREATE TABLE IF NOT EXISTS constituency_issues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link to constituency (optional for demo)
    constituency_id UUID,

    -- Issue details
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL, -- Maps to issue_categories.code (WATER, EDUCATION, etc.)
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL CHECK (status IN ('reported', 'acknowledged', 'in_progress', 'resolved', 'closed')) DEFAULT 'reported',

    -- Location
    location TEXT NOT NULL,
    coordinates JSONB, -- {lat: number, lng: number}

    -- Reporter
    reported_by UUID REFERENCES auth.users(id),
    reported_at TIMESTAMPTZ DEFAULT NOW(),

    -- Engagement
    supporters INT DEFAULT 0,
    comments_count INT DEFAULT 0,

    -- Assignment & Resolution
    assigned_to TEXT,
    estimated_resolution DATE,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes
CREATE INDEX idx_constituency_issues_constituency ON constituency_issues(constituency_id);
CREATE INDEX idx_constituency_issues_category ON constituency_issues(category);
CREATE INDEX idx_constituency_issues_status ON constituency_issues(status);
CREATE INDEX idx_constituency_issues_reported_by ON constituency_issues(reported_by);
CREATE INDEX idx_constituency_issues_created_at ON constituency_issues(created_at DESC);

-- RLS Policies
ALTER TABLE constituency_issues ENABLE ROW LEVEL SECURITY;

-- Anyone can view issues
CREATE POLICY "constituency_issues_select_all" ON constituency_issues
    FOR SELECT
    TO public
    USING (true);

-- Authenticated users can insert issues
CREATE POLICY "constituency_issues_insert_authenticated" ON constituency_issues
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Users can update their own issues
CREATE POLICY "constituency_issues_update_own" ON constituency_issues
    FOR UPDATE
    TO authenticated
    USING (reported_by = auth.uid())
    WITH CHECK (reported_by = auth.uid());

-- Admins can update any issue
CREATE POLICY "constituency_issues_update_admin" ON constituency_issues
    FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'superadmin', 'manager')
        )
    );

-- Grant permissions
GRANT ALL ON constituency_issues TO authenticated;
GRANT SELECT ON constituency_issues TO anon;

-- =====================================================
-- INSERT SAMPLE DATA FOR DEMONSTRATION
-- =====================================================

INSERT INTO constituency_issues (
    title, description, category, priority, status, location, supporters, comments_count, reported_at
) VALUES
(
    'Poor Street Lighting on MG Road',
    'Several street lights have been non-functional for over 2 months, creating safety concerns for evening commuters and pedestrians.',
    'INFRASTRUCTURE',
    'high',
    'acknowledged',
    'MG Road, Near Central Station',
    23,
    8,
    NOW() - INTERVAL '5 days'
),
(
    'Overcrowding at Government Hospital',
    'Long waiting times at the OPD, insufficient seating arrangements, and need for additional consultation rooms.',
    'HEALTHCARE',
    'urgent',
    'in_progress',
    'Government General Hospital',
    67,
    15,
    NOW() - INTERVAL '7 days'
),
(
    'Need for Children''s Park in Residential Area',
    'The Pattom residential area lacks recreational facilities for children. Request for establishing a small park with playground equipment.',
    'INFRASTRUCTURE',
    'medium',
    'reported',
    'Pattom Residential Complex',
    43,
    12,
    NOW() - INTERVAL '2 days'
),
(
    'Irregular Water Supply',
    'Water supply has been irregular for the past month. Many households receiving water only on alternate days.',
    'WATER',
    'high',
    'acknowledged',
    'Vazhuthacaud Area',
    89,
    23,
    NOW() - INTERVAL '8 days'
);

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Check if table exists and has data
SELECT
    COUNT(*) as total_issues,
    COUNT(CASE WHEN status = 'reported' THEN 1 END) as reported,
    COUNT(CASE WHEN status = 'acknowledged' THEN 1 END) as acknowledged,
    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
    COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved
FROM constituency_issues;

-- Check sample data
SELECT id, title, category, priority, status, supporters, location
FROM constituency_issues
ORDER BY reported_at DESC;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '✅ CONSTITUENCY ISSUES TABLE CREATED SUCCESSFULLY';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Table: constituency_issues';
    RAISE NOTICE 'Sample Data: 4 demo issues inserted';
    RAISE NOTICE 'RLS: Enabled with proper policies';
    RAISE NOTICE 'Indexes: Created for performance';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Step: Refresh browser and check My Constituency page';
    RAISE NOTICE '============================================================================';
END $$;
