# Deployment Instructions - Pulse of People

## 🚀 Quick Deploy to Render

### Step 1: Push the New Dockerfile

```bash
# Add the new Dockerfile in repository root
git add Dockerfile .dockerignore

# Commit
git commit -m "Add simplified production Dockerfile for Render"

# Push to GitHub
git push origin main
```

### Step 2: Configure Render Service

In your Render dashboard:

1. **Go to your service settings**
2. **Update these settings**:
   ```
   Root Directory: (leave empty - use repo root)
   Dockerfile Path: ./Dockerfile
   Docker Command: (leave empty - uses CMD from Dockerfile)
   ```

3. **Add Environment Variables**:
   ```
   VITE_SUPABASE_URL = https://iwtgbseaoztjbnvworyq.supabase.co
   VITE_SUPABASE_ANON_KEY = your-anon-key-here
   VITE_APP_URL = https://pulseofpeople.onrender.com
   VITE_APP_NAME = Pulse of People
   ```

4. **Deploy**:
   - Click "Manual Deploy"
   - Select "Clear build cache & deploy"
   - Wait for build to complete

---

## 📦 What the New Dockerfile Does

```dockerfile
FROM node:18-alpine          # Lightweight Node image
WORKDIR /app                 # Set working directory
COPY frontend/package*.json  # Copy package files
RUN npm install              # Install dependencies
COPY frontend/ ./            # Copy source code
RUN npm run build            # Build production bundle
RUN npm install -g serve     # Install static file server
EXPOSE 3000                  # Expose port
CMD ["serve", "-s", "dist"]  # Serve built files
```

**Benefits**:
- ✅ Single-stage build (simpler)
- ✅ Uses repository root (no subdirectory issues)
- ✅ Production build with Vite
- ✅ Lightweight serve package
- ✅ Port 3000 (Render compatible)

---

## 🔍 Verify Deployment

After deployment succeeds:

1. **Check Build Logs**:
   ```
   ✓ npm install completed
   ✓ npm run build completed
   ✓ Container started
   ```

2. **Test Health**:
   ```bash
   curl https://pulseofpeople.onrender.com
   # Should return HTML
   ```

3. **Open in Browser**:
   ```
   https://pulseofpeople.onrender.com
   ```

4. **Verify Features**:
   - [ ] Dashboard loads
   - [ ] Supabase data appears
   - [ ] Charts render correctly
   - [ ] No console errors

---

## 🐛 Troubleshooting

### Build Fails with "Cannot find package.json"?

**Fix**: Verify the Dockerfile is in the **repository root** (not frontend folder)

```bash
# Check location
ls -la Dockerfile  # Should be in repo root
```

### Environment Variables Not Working?

**Fix**: Ensure variables start with `VITE_` and are set **before** deployment:

```bash
# In Render dashboard
VITE_SUPABASE_URL = https://...  (not SUPABASE_URL)
```

### Port Issues?

The Dockerfile uses port 3000. Render will automatically map this to HTTPS port 443.

### Still Not Working?

**Test locally with Docker**:

```bash
# Build
docker build -t pulseofpeople .

# Run
docker run -p 3000:3000 \
  -e VITE_SUPABASE_URL=https://your-url \
  -e VITE_SUPABASE_ANON_KEY=your-key \
  pulseofpeople

# Visit http://localhost:3000
```

---

## 🎯 Alternative: Deploy to Vercel (Recommended)

Vercel is **much easier** for Vite apps:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Follow prompts:
# - Link to existing project? No
# - Project name? pulseofpeople
# - Directory? ./ (current)
# - Override settings? No

# ✅ Deployed!
```

**Then add environment variables** in Vercel dashboard:
- VITE_SUPABASE_URL
- VITE_SUPABASE_ANON_KEY
- VITE_APP_URL
- VITE_APP_NAME

**Redeploy**: `vercel --prod`

---

## 📊 Deployment Comparison

| Feature | Render (Docker) | Vercel |
|---------|-----------------|--------|
| Setup Complexity | Medium | Easy |
| Build Time | 2-3 mins | 30-60s |
| Auto SSL | ✅ | ✅ |
| Custom Domain | ✅ | ✅ |
| Environment Variables | Manual | Dashboard |
| Auto Deploy on Push | ✅ | ✅ |
| Free Tier | 750 hrs/month | Unlimited |
| Best For | Docker apps | Static sites/SPA |

**Recommendation**: Use **Vercel** for this Vite app - it's designed for it!

---

## ✅ Success Checklist

- [ ] Dockerfile in repository root
- [ ] .dockerignore file created
- [ ] Changes committed and pushed
- [ ] Render service configured
- [ ] Environment variables added
- [ ] Build completed successfully
- [ ] Application accessible via URL
- [ ] Dashboard loads with real data
- [ ] No console errors

---

## 📞 Need Help?

**Render Support**: https://render.com/docs/deploy-node-express-app
**Vercel Docs**: https://vercel.com/docs/frameworks/vite

---

**Created**: November 9, 2025
**Status**: Ready to Deploy
**Next Step**: `git add . && git commit -m "Add production Dockerfile" && git push`
