# Sellandiamman Traders - Hostinger Deployment Guide

## Production Domain: https://www.sellandiammantraders.com

---

## 📦 STEP 1: Build the Frontend

```bash
cd frontend
npm run build
```

This creates a `build/` folder with all static files.

---

## 📤 STEP 2: Upload Frontend to Hostinger

1. **Login to Hostinger** → File Manager → `public_html/`
2. **Delete all old files** in `public_html/` (backup first if needed)
3. **Upload contents of `build/` folder** to `public_html/`
   - Upload ALL files including hidden `.htaccess`
   
Your `public_html/` should look like:
```
public_html/
├── .htaccess          ← CRITICAL for React routing!
├── index.html
├── manifest.json
├── robots.txt
├── sitemap.xml
├── favicon.svg
├── og-image.png
├── static/
│   ├── css/
│   └── js/
└── ...
```

---

## 🔧 STEP 3: Backend Deployment Options

### Option A: Hostinger VPS (Recommended)

1. **Install Python 3.11+** on your VPS
2. **Upload backend folder** to `/var/www/backend/`
3. **Install dependencies:**
   ```bash
   cd /var/www/backend
   pip install -r requirements.txt
   ```
4. **Configure environment:**
   ```bash
   cp .env.production .env
   nano .env  # Edit with your actual credentials
   ```
5. **Run with Gunicorn:**
   ```bash
   pip install gunicorn uvicorn
   gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
   ```
6. **Set up systemd service** (create `/etc/systemd/system/sellandiamman.service`):
   ```ini
   [Unit]
   Description=Sellandiamman Traders API
   After=network.target
   
   [Service]
   User=www-data
   WorkingDirectory=/var/www/backend
   ExecStart=/usr/local/bin/gunicorn server:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
7. **Configure Nginx** to proxy `/api` to the backend

### Option B: Shared Hosting (Limited)

Shared hosting doesn't support Python backends. You would need to:
- Use a separate backend hosting (Railway, Render, etc.)
- Update REACT_APP_BACKEND_URL to point to that service

---

## 🗄️ STEP 4: Database Setup

The MySQL database is already configured on Hostinger:
- **Host:** `localhost` (when accessed from Hostinger server)
- **Database:** `u217264814_Sellandiamman`
- **User:** `u217264814_sellandiamman`

Tables are already created. If you need to recreate:
1. Go to **phpMyAdmin** in Hostinger
2. Import `/backend/schema.sql`

---

## 🌐 STEP 5: DNS & SSL Configuration

1. **Point domain to Hostinger:**
   - Set A record: `@` → Hostinger IP
   - Set A record: `www` → Hostinger IP

2. **Enable SSL:**
   - Hostinger → SSL/TLS → Enable Free SSL
   - Force HTTPS redirect (already in .htaccess)

---

## ✅ STEP 6: Post-Deployment Checklist

Test these URLs:
- [ ] https://www.sellandiammantraders.com/ (Homepage)
- [ ] https://www.sellandiammantraders.com/catalogue (Catalogue)
- [ ] https://www.sellandiammantraders.com/contact (Contact)
- [ ] https://www.sellandiammantraders.com/login (Login page)
- [ ] Refresh any page - should NOT show 404

Test functionality:
- [ ] Login with admin@sellandiamman.com / admin123
- [ ] View products
- [ ] Create an order
- [ ] Check browser DevTools → Network → No CORS errors

Check SEO:
- [ ] View page source → canonical URL is production domain
- [ ] https://www.sellandiammantraders.com/robots.txt works
- [ ] https://www.sellandiammantraders.com/sitemap.xml works

---

## 🔐 Security Reminders

1. **Change default admin password** after first login
2. **Update JWT_SECRET** in production `.env`
3. **Never commit `.env` files** to git
4. **Enable Hostinger firewall** if available
5. **Set up regular database backups**

---

## 🆘 Troubleshooting

### Login not working?
- Check browser DevTools → Network tab
- Verify API calls go to correct domain
- Check CORS settings in backend

### 404 on page refresh?
- Ensure `.htaccess` is uploaded to `public_html/`
- Check if mod_rewrite is enabled on Hostinger

### Products not loading?
- Verify database connection in backend
- Check backend logs for errors
- Ensure MySQL remote access is enabled

### CORS errors?
- Update `CORS_ORIGINS` in backend `.env`
- Restart backend service

---

## 📞 Support

For technical issues with the application code, check:
- Backend logs: `tail -f /var/log/backend.log`
- Browser console for frontend errors

---

**Admin Login:**
- Email: admin@sellandiamman.com
- Password: admin123 (CHANGE THIS!)
