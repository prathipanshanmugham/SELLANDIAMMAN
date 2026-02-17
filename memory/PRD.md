# Sellandiamman Traders - Inventory & Sales Management System

## Original Problem Statement
Build a private inventory + sales + picking management system for Sellandiamman Traders (Electrical Retail & Wholesale Store) with 10,000+ products capacity. Key goals: Faster billing, faster product locating, accurate stock tracking, efficient picking, no stock visibility to customers.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + qrcode.react
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (collections: products, employees, orders, stock_transactions, presence_logs)
- **Authentication**: JWT-based (Admin/Staff roles)

## User Personas
1. **Admin**: Full access - products, locations, staff, reports, orders, staff presence management
2. **Staff**: Limited - search, create orders, picklists, mark picked (cannot change presence)

## Core Requirements
- [x] Public website (Home, Catalogue, Contact) - NO stock visibility
- [x] JWT Authentication with Admin/Staff roles
- [x] Product management with auto-generated location codes
- [x] Order/Picklist workflow with "Mark as Picked"
- [x] Auto stock deduction
- [x] Admin dashboard with charts (Recharts)
- [x] Low stock alerts
- [x] Print-friendly picklist view (thermal receipt optimized)
- [x] Full mobile responsiveness
- [x] Master QR Barcode on receipts for billing software integration
- [x] Staff Live Presence System (Admin-controlled)
- [x] **Compact Receipt Format** - Dynamic height, one-line items
- [x] **Price Display in Catalogue** - Shows price publicly (still hides stock/location)

## What's Been Implemented

### Feb 17, 2026 - Compact Receipt & Price Display

**1. Compact Receipt Format**
- Dynamic height: `@page { size: 80mm auto; }`
- One-line item format: `Product | CompactLocation | xQty`
- Compressed location codes: A-03-R07-S2-B05 → A03R07S2B05
- Smaller QR code in print (80px vs 180px on screen)
- Minimal footer with item count and timestamp
- 30-50% paper reduction

**2. Price Display in Public Catalogue**
- Products now have: selling_price, mrp, unit, gst_percentage
- Catalogue shows: ₹85/meter (with ₹100 strikethrough if MRP higher)
- "Price on request" for products with price = 0
- Stock quantity and location still hidden from public
- Product form has Pricing Information section

**3. QR Barcode & Staff Presence**
- Master QR Barcode on receipts
- Staff Live Monitor panel on dashboard
- Admin-only presence control (5 states)

### Feb 16, 2026 - Mobile Responsiveness
- Mobile hamburger menu for public pages
- Card-based views for all admin/staff tables
- Responsive dashboard stats

## Product Data Model
```javascript
{
  id: string,
  sku: string,
  product_name: string,
  category: string,
  brand: string,
  zone: string,
  aisle: int,
  rack: int,
  shelf: int,
  bin: int,
  full_location_code: string,
  quantity_available: int,
  reorder_level: int,
  supplier: string,
  image_url: string,
  // Price fields
  selling_price: float,  // Display price
  mrp: float,            // Max retail price (shows strikethrough)
  unit: string,          // piece, meter, kg, box, set, roll, pack
  gst_percentage: float, // 0, 5, 12, 18, 28
  last_updated: datetime
}
```

## Receipt Format (Print)
```
SELLANDIAMMAN TRADERS
─────────────────────────
ORD-20260217-0001 | 17/02 10:30 | Customer Name
─────────────────────────
1. 2.5sqmm Copper Wire | A03R07S2B05 | x10
2. 32A MCB Single Pole | B02R05S3B08 | x5
─────────────────────────
        [QR CODE]
Scan for Bill | 2 items | 17/02 10:30
           Thank You!
```

## API Endpoints

### Public (No Auth)
- `GET /api/public/catalogue` - Returns: sku, product_name, category, brand, image_url, selling_price, mrp, unit
- `GET /api/public/categories` - Category list

### Products (Auth Required)
- Full CRUD with all fields including price

### Dashboard
- `GET /api/dashboard/staff-presence` - Staff presence data

### Employees
- `PATCH /api/employees/{id}/presence` - Update presence (admin only)
- `GET /api/employees/presence-log` - Status change history

## Key Files
- `frontend/src/pages/public/CataloguePage.js` - Price display UI
- `frontend/src/pages/admin/ProductFormPage.js` - Pricing form section
- `frontend/src/pages/staff/PicklistPage.js` - Compact print format
- `frontend/src/pages/admin/AdminDashboard.js` - Staff Live Monitor
- `backend/server.py` - All API endpoints with price models

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] All core features
- [x] Mobile responsiveness
- [x] QR Barcode & Presence System
- [x] Compact Receipt Format
- [x] Price in Catalogue

### P1 (Important) - Pending
- [ ] PDF download for picklists
- [ ] Barcode scanner integration
- [ ] GST invoice generation

### P2 (Nice to Have)
- [ ] Bulk product import
- [ ] Multi-branch support
- [ ] Supplier purchase orders

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123

## Sample Products with Prices
| SKU | Product | Price | MRP | Unit |
|-----|---------|-------|-----|------|
| WIRE001 | 2.5 Sqmm Copper Wire | ₹85 | ₹100 | meter |
| MCB001 | 32A MCB Single Pole | ₹450 | ₹550 | piece |
| DRILL01 | Cordless Drill 18V | ₹2,499 | ₹2,999 | piece |
| SWITCH01 | 6A Switch Socket | Price on request | - | piece |
