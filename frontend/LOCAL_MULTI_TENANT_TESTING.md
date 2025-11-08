# Local Multi-Tenant Testing Guide

## Quick Setup for Local Subdomain Testing

### 1. Update Your Hosts File

Add these entries to your hosts file to enable subdomain testing locally:

**Windows:** `C:\Windows\System32\drivers\etc\hosts`
**Mac/Linux:** `/etc/hosts`

```
127.0.0.1 party-a.localhost
127.0.0.1 party-b.localhost
127.0.0.1 localhost
```

### 2. Start Development Server

```bash
npm run dev
```

The server will start on port 5173.

### 3. Access Different Tenants

Once the database is set up with tenant data, you can access:

- **Default/No Tenant:** http://localhost:5173
- **Party A:** http://party-a.localhost:5173
- **Party B:** http://party-b.localhost:5173

### 4. Testing Tenant Detection

The application will automatically detect the tenant from the subdomain:
- `party-a.localhost` → Tenant slug: `party-a`
- `party-b.localhost` → Tenant slug: `party-b`

### 5. Development Testing with URL Parameters

For easier development testing without modifying hosts file, you can also use URL parameters:

- http://localhost:5173?tenant=party-a
- http://localhost:5173?tenant=party-b

### 6. Verify Tenant Context

Once logged in, you can verify the current tenant by:
1. Opening browser DevTools (F12)
2. Going to Console
3. The app will log: "Current tenant: [tenant-name]"

### 7. Testing Cross-Tenant Isolation

1. Open two browser windows (use Incognito for one)
2. Login to Party A in first window: http://party-a.localhost:5173
3. Login to Party B in second window: http://party-b.localhost:5173
4. Verify that data is completely isolated between tenants

## Troubleshooting

### Subdomain Not Working
- Ensure hosts file is saved with admin privileges
- Clear browser cache
- Try using incognito mode
- Restart browser after hosts file changes

### Tenant Not Detected
- Check browser console for errors
- Ensure VITE_MULTI_TENANT=true in .env
- Verify TenantProvider is properly integrated

### SSL Warnings
- Local development uses HTTP, SSL warnings are normal
- In production, Vercel will handle SSL automatically

## Next Steps

After local testing works:
1. Run database migration to create tenant tables
2. Create tenant records in database
3. Test with actual tenant data
4. Deploy to staging environment