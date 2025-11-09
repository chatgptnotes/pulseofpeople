# Render Deployment Fix Guide
## Issue: Dockerfile Not Found Error

**Error**: `failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory`

**Root Cause**: Render is looking for the Dockerfile in the repository root, but it's located in the `frontend/` subdirectory.

---

## ✅ **Solution: Update Render Configuration**

### Option 1: Use Render Dashboard (Easiest)

1. **Go to your Render service** at https://dashboard.render.com
2. **Click on your service** (pulseofpeople-frontend)
3. **Go to Settings**
4. **Update the following**:

```
Root Directory: frontend
Docker Build Context: frontend
Dockerfile Path: ./Dockerfile
```

5. **Add Environment Variables**:
   - `VITE_SUPABASE_URL` = Your Supabase project URL
   - `VITE_SUPABASE_ANON_KEY` = Your Supabase anon key
   - `VITE_APP_URL` = Your app URL (e.g., https://pulseofpeople.onrender.com)
   - `VITE_APP_NAME` = Pulse of People

6. **Save and redeploy**

---

### Option 2: Use render.yaml Blueprint (Recommended)

I've created a `render.yaml` file in the `frontend/` directory. Move it to the repository root:

```bash
# Move render.yaml to repository root
mv frontend/render.yaml render.yaml

# Commit and push
git add render.yaml
git commit -m "Add Render blueprint configuration"
git push origin main
```

Then in Render:
1. **Delete the current service**
2. **Create New > Blueprint**
3. **Connect your GitHub repository**
4. **Render will auto-detect the render.yaml**
5. **Add the environment variables**
6. **Deploy**

---

### Option 3: Modify Render Service via CLI

If you're using the Render CLI:

```bash
# Update service settings
render services update pulseofpeople-frontend \
  --root-dir=frontend \
  --dockerfile-path=./Dockerfile \
  --docker-context=.
```

---

## 🐳 **Verify Dockerfile Configuration**

Your Dockerfile is already correctly configured:

**Location**: `/frontend/Dockerfile`

**Build Process**:
1. ✅ Uses Node 22 Alpine for building
2. ✅ Installs dependencies with `npm install`
3. ✅ Builds the Vite app with `npm run build`
4. ✅ Serves with Nginx in production
5. ✅ Multi-stage build for optimized image size
6. ✅ Runs as non-root user for security
7. ✅ Includes health check endpoint

**Nginx Configuration**: `/frontend/nginx.conf`
- ✅ SPA routing with fallback to index.html
- ✅ Static asset caching
- ✅ Gzip compression
- ✅ Security headers
- ✅ Health check at `/health`

---

## 📋 **Required Environment Variables**

Make sure these are set in Render:

```env
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=<your-anon-key>
VITE_APP_URL=https://pulseofpeople.onrender.com
VITE_APP_NAME=Pulse of People
```

**Important**: These must be set **before** build time, as Vite embeds them during the build process.

---

## 🚀 **Deployment Steps**

### Method 1: Dashboard Deployment

1. **Fix Configuration** (as described above)
2. **Trigger Manual Deploy**:
   - Go to your service
   - Click "Manual Deploy"
   - Select "Clear build cache & deploy"
3. **Monitor Build Logs**
4. **Verify Deployment**

### Method 2: Git Push Deployment

```bash
# Ensure all changes are committed
git add .
git commit -m "Configure Render deployment"
git push origin main

# Render will auto-deploy
```

---

## 🔍 **Verify Deployment Success**

After deployment, verify:

1. **Build Logs**: Check for successful build
   ```
   ✓ Stage 1: Build completed
   ✓ Stage 2: Nginx image created
   ✓ Health check passed
   ```

2. **Service URL**: Visit your Render URL
   ```
   https://pulseofpeople.onrender.com
   ```

3. **Health Check**: Test the health endpoint
   ```bash
   curl https://pulseofpeople.onrender.com/health
   # Should return: healthy
   ```

4. **Application**: Verify the dashboard loads with real data

---

## 🐛 **Troubleshooting**

### Build Still Failing?

1. **Check Root Directory**:
   ```
   Root Directory: frontend  (not ./frontend or /frontend)
   ```

2. **Check Docker Context**:
   ```
   Docker Context: .  (current directory)
   ```

3. **Verify Files Exist**:
   ```bash
   # In your repository
   ls -la frontend/Dockerfile
   ls -la frontend/nginx.conf
   ls -la frontend/package.json
   ```

### Environment Variables Not Working?

1. **Rebuild with Clear Cache**:
   - Render Dashboard > Settings > Clear build cache & deploy

2. **Check Variable Names**:
   - Must start with `VITE_`
   - Exact spelling matters

3. **Check Build Logs**:
   - Ensure variables are available during build
   - Look for "Building for production..."

### Port Issues?

The Dockerfile exposes port 80. Render will automatically map this to HTTPS.

---

## 📊 **Expected Build Output**

```
==> Cloning from https://github.com/chatgptnotes/pulseofpeople
==> Checking out commit in branch main
==> Building Docker image
#1 [internal] load build definition from Dockerfile
#1 DONE
#2 [internal] load metadata
#2 DONE
#3 [stage-0] FROM node:22-alpine
#3 DONE
#4 [stage-0] WORKDIR /app
#4 DONE
#5 [stage-0] COPY package*.json ./
#5 DONE
#6 [stage-0] RUN npm install
#6 DONE
#7 [stage-0] COPY . .
#7 DONE
#8 [stage-0] RUN npm run build
#8 DONE
#9 [stage-1] FROM nginx:alpine
#9 DONE
#10 [stage-1] COPY nginx.conf /etc/nginx/conf.d/default.conf
#10 DONE
#11 [stage-1] COPY --from=builder /app/dist /usr/share/nginx/html
#11 DONE
==> Build successful
==> Starting service
==> Service is live at https://pulseofpeople.onrender.com
```

---

## 🎯 **Quick Fix Checklist**

- [ ] Set Root Directory to `frontend`
- [ ] Set Dockerfile Path to `./Dockerfile`
- [ ] Set Docker Context to `.`
- [ ] Add all VITE_* environment variables
- [ ] Clear build cache
- [ ] Redeploy
- [ ] Verify health endpoint
- [ ] Test application functionality

---

## 📞 **Still Having Issues?**

If the deployment still fails:

1. **Check Render Status**: https://status.render.com
2. **Review Build Logs**: Look for specific error messages
3. **Test Locally**:
   ```bash
   cd frontend
   docker build -t pulseofpeople .
   docker run -p 8080:80 pulseofpeople
   # Visit http://localhost:8080
   ```

4. **Contact Render Support** with:
   - Service URL
   - Build logs
   - Repository link

---

## ✅ **Alternative: Deploy to Vercel Instead**

Vercel is **easier** for Vite apps (no Docker needed):

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel --prod

# Follow prompts
# ✓ Deployed to https://pulseofpeople.vercel.app
```

**Vercel automatically**:
- Detects Vite configuration
- Builds with correct settings
- Handles environment variables
- Provides instant SSL
- No Docker configuration needed

---

**Created**: November 9, 2025
**Status**: Ready to Deploy
**Next Step**: Update Render settings and redeploy
