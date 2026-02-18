# Sellandiamman Traders - Inventory & Sales Management System

## Original Problem Statement
Build a private inventory + sales + picking management system for Sellandiamman Traders (Electrical Retail & Wholesale Store) with 10,000+ products capacity.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + react-barcode
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Authentication**: JWT-based (Admin/Staff roles)

## Latest Updates

### Feb 18, 2026 - Item-Level SKU Barcodes

**Changed Barcode System:**
- ❌ Removed: Master QR code with JSON/Order ID
- ✅ Added: Individual Code128 barcode per item with SKU only

**New Receipt Format:**
```
SELLANDIAMMAN TRADERS
------------------------------
2.5sqmm Copper Wire
A03R07S2B05 | x10
|||||||||||||||||||
     ELX1023
------------------------------
Switch 6A
B02R05S3B08 | x5
|||||||||||||||||||
     SWI2023
------------------------------
2 items | 18/02 10:30
Thank You!
```

**How Billing Works:**
1. Scan SKU barcode
2. Enter quantity manually in POS
3. Repeat for each item

**Barcode Config:**
- Format: Code128
- Screen: width=1.5, height=40
- Print: width=1.2, height=25
- Value: SKU only (e.g., WIRE001, MCB001)

### Earlier Features
- Order ID Input + Auto Sequence (ORD-0001, ORD-0002...)
- POS thermal print fix (no blank paper)
- Price display in catalogue
- Staff Live Presence System
- Full mobile responsiveness

## Key Features

### Barcode System (Industry Standard)
- One barcode per product (not per order)
- Code128 format - compatible with all scanners
- SKU only - no JSON, no encryption
- Works with: Odoo, Zoho, Tally, any POS

### Order ID System
- Format: ORD-0001 (4-digit sequence)
- Auto-generate on page load
- "Generate Next" button
- Manual entry allowed

### Price Display
- Public catalogue shows: ₹85/meter
- MRP strikethrough when discount
- Stock/location hidden from public

### Staff Presence
- Admin-only control
- 5 states: Present, Permission, On Field, Absent, On Leave
- Live Monitor on Dashboard

## API Endpoints

### Orders
- `GET /api/orders/next-order-id` - Next sequential ID
- `POST /api/orders` - Create (optional custom order_id)
- `GET /api/orders/{id}` - Get with items

### Products
- Full CRUD with price fields
- Public catalogue (no stock/location)

### Dashboard
- Stats, charts, staff presence

## Print Receipt (Thermal 80mm)

**CSS:**
```css
@page { size: 80mm auto; margin: 0; }
.receipt { height: auto; page-break-inside: avoid; }
```

**Structure:**
1. Header: Store name
2. Order info: ID | Date | Customer
3. Items: Name, Location, Qty, Barcode
4. Footer: Item count, Thank You

## Key Files
- `frontend/src/pages/staff/PicklistPage.js` - Item-level barcodes
- `frontend/src/pages/staff/CreateOrder.js` - Order ID input
- `frontend/src/pages/public/CataloguePage.js` - Price display
- `frontend/src/pages/admin/AdminDashboard.js` - Staff Monitor

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123

## Completed Features ✅
- All core inventory features
- Mobile responsiveness
- Order ID sequence
- Item-level SKU barcodes
- Thermal print optimization
- Price in catalogue
- Staff presence system

## Pending Features
- [ ] PDF download for picklists
- [ ] Barcode scanner hardware integration
- [ ] GST invoice generation
- [ ] Bulk product import
