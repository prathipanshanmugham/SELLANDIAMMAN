# Sellandiamman Traders - Vercel Backend Deployment

## Step 1: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

## Step 2: Deploy Backend

### Option A: Deploy via CLI
```bash
cd vercel-backend
npm i -g vercel
vercel login
vercel
```

### Option B: Deploy via GitHub
1. Push `vercel-backend` folder to GitHub
2. Import project in Vercel dashboard
3. Vercel auto-detects Python

## Step 3: Set Environment Variables in Vercel

Go to **Project Settings → Environment Variables** and add:

| Variable | Value |
|----------|-------|
| `MYSQL_HOST` | `82.25.121.84` |
| `MYSQL_USER` | `u217264814_sellandiamman` |
| `MYSQL_PASSWORD` | `Sellandiamman2017` |
| `MYSQL_DATABASE` | `u217264814_Sellandiamman` |
| `JWT_SECRET` | `your-secure-secret-key` |
| `CORS_ORIGINS` | `https://www.sellandiammantraders.com,https://sellandiammantraders.com` |

## Step 4: Whitelist Vercel IPs in Hostinger

Vercel uses dynamic IPs. In Hostinger MySQL:
1. Go to **Databases → Remote MySQL**
2. Add: `%` (allow all) OR specific Vercel IPs

## Step 5: Get Your Backend URL

After deployment, Vercel gives you a URL like:
```
https://your-project.vercel.app
```

## Step 6: Update Frontend

Update `frontend/.env.production`:
```
REACT_APP_BACKEND_URL=https://your-project.vercel.app
```

Then rebuild:
```bash
cd frontend
npm run build
```

## Step 7: Deploy Frontend to Hostinger

Upload `frontend/build/*` to Hostinger `public_html/`

---

## API Endpoints Available

- `GET /api/health` - Health check
- `POST /api/auth/login` - Login
- `GET /api/products` - Get products
- `GET /api/orders` - Get orders
- etc.

## Test Your Deployment

```bash
curl https://your-project.vercel.app/api/health
```

Should return: `{"status":"healthy"}`
