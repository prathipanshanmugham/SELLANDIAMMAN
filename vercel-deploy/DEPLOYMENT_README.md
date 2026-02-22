# Vercel Deployment Guide for Sellandiamman Traders

## Deployment Package Location
The complete deployment package is at: `/app/vercel-deploy/`

## Contents
- `index.html` - React frontend (production build)
- `static/` - Frontend assets (JS, CSS)
- `api/index.py` - Backend API (Python serverless function)
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel configuration

## Step-by-Step Deployment

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI (if not installed):
   ```bash
   npm i -g vercel
   ```

2. Navigate to deployment folder:
   ```bash
   cd /app/vercel-deploy
   ```

3. Deploy:
   ```bash
   vercel --prod
   ```

4. When prompted, set these environment variables in Vercel dashboard:
   - `MYSQL_HOST` = `82.25.121.84`
   - `MYSQL_USER` = `u217264814_sellandiamman`
   - `MYSQL_PASSWORD` = `Sellandiamman2017`
   - `MYSQL_DATABASE` = `u217264814_Sellandiamman`
   - `JWT_SECRET` = `sellandiamman-traders-secret-key-2024-secure`

### Option 2: Deploy via GitHub

1. Create a new GitHub repository
2. Copy all contents from `/app/vercel-deploy/` to the repository
3. Connect the repository to Vercel
4. Add the environment variables in Vercel Dashboard → Settings → Environment Variables

### Option 3: Deploy via Vercel Dashboard (Drag & Drop)

1. Go to https://vercel.com/new
2. Choose "Import from an existing project" or "Deploy without Git"
3. Upload the `/app/vercel-deploy/` folder
4. Add environment variables before deploying

## Environment Variables Required

| Variable | Value |
|----------|-------|
| MYSQL_HOST | 82.25.121.84 |
| MYSQL_USER | u217264814_sellandiamman |
| MYSQL_PASSWORD | Sellandiamman2017 |
| MYSQL_DATABASE | u217264814_Sellandiamman |
| JWT_SECRET | sellandiamman-traders-secret-key-2024-secure |

**IMPORTANT:** These must be set BEFORE deployment or the API will fail.

## Testing After Deployment

1. Test health endpoint:
   ```bash
   curl https://your-vercel-url.vercel.app/api/health
   ```

2. Test frontend:
   Open https://your-vercel-url.vercel.app/ in browser

3. Test login:
   - Email: admin@sellandiamman.com
   - Password: admin123

## Troubleshooting

If you see "FUNCTION_INVOCATION_FAILED":
1. Check Vercel Dashboard → Functions → Logs
2. Verify all environment variables are set correctly
3. Ensure MYSQL_HOST allows external connections (Hostinger firewall)

If you see 404 on frontend:
1. Ensure index.html is in the root of deployment
2. Check vercel.json routes configuration
