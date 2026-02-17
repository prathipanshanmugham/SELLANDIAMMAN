# Sellandiamman Traders - Inventory & Sales Management System

## Original Problem Statement
Build a private inventory + sales + picking management system for Sellandiamman Traders (Electrical Retail & Wholesale Store) with 10,000+ products capacity. Key goals: Faster billing, faster product locating, accurate stock tracking, efficient picking, no stock visibility to customers.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + qrcode.react
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB (collections: products, employees, orders, stock_transactions, presence_logs)
- **Authentication**: JWT-based (Admin/Staff roles)

## What's Been Implemented

### Feb 17, 2026 - Latest Features

**1. Order ID Input + Auto Sequence**
- Format: ORD-0001, ORD-0002, ORD-0003... (simple 4-digit sequence)
- Auto-generates on page load
- "Generate Next" button fetches next sequential ID
- Manual entry allowed (must be unique, auto-uppercase)
- API: `GET /api/orders/next-order-id`

**2. POS Thermal Printing Fix (No Blank Paper)**
```css
@page { size: 80mm auto !important; margin: 0 !important; }
.receipt { height: auto !important; page-break-inside: avoid !important; }
```
- Dynamic height based on content
- No forced page breaks
- No extra margins/padding
- Compact one-line item format

**3. Master QR Code Plain Text Format**
- Changed from JSON to plain text SKUs
- Format: `#ORD-0001\nSKU1\nSKU1\nSKU2` (SKU repeated for qty)
- Works with barcode scanners as keyboard input
- Each scan sends: SKU1 [ENTER] SKU2 [ENTER]...
- Compatible with: Odoo, Zoho, Tally, any POS

**4. Price Display in Catalogue**
- Products have: selling_price, mrp, unit, gst_percentage
- Shows ₹85/meter with ₹100 strikethrough
- Stock/location hidden from public

**5. Staff Live Presence System**
- Admin-only status control: Present, Permission, On Field, Absent, On Leave
- Live Monitor panel on Dashboard
- Status change history logging

### Earlier Features
- JWT Authentication (Admin/Staff roles)
- Full product CRUD with location codes
- Order/Picklist workflow with "Mark as Picked"
- Auto stock deduction
- Mobile responsiveness
- SEO optimization
- WhatsApp button

## QR Code Format

**New Plain Text Format (Scanner Compatible):**
```
#ORD-0001
WIRE001
WIRE001
WIRE001
MCB001
```
- First line: Order ID prefix
- Each SKU on new line
- SKU repeated for quantity (WIRE001 x3 = 3 lines)
- Scanner sends each as keyboard input + Enter

**Why This Format:**
- Scanners act as keyboard emulation
- Each newline = Enter key
- Billing software receives: SKU1 [ENTER] SKU2 [ENTER]
- Auto-adds items one by one
- Works with any POS system

## Print Receipt Format (Thermal 80mm)

```
SELLANDIAMMAN TRADERS
─────────────────────
ORD-0001 | 17/02 10:30 | Customer
─────────────────────
1. 2.5sqmm Copper Wire | A03R07S2B05 | x10
2. 32A MCB Single Pole | B02R05S3B08 | x5
─────────────────────
      [QR CODE]
Scan for Bill | 15 items
    Thank You!
```

- One-line item format
- Compressed location codes
- Dynamic height (no blank paper)
- 70px QR code in print

## API Endpoints

### Orders
- `GET /api/orders/next-order-id` - Get next sequential ORD-XXXX
- `POST /api/orders` - Create order (accepts optional `order_id`)
- `GET /api/orders` - List orders
- `GET /api/orders/{id}` - Get order with picklist
- `PATCH /api/orders/{id}/items/{item_id}/pick` - Mark picked

### Products
- Full CRUD with price fields
- Public catalogue (no stock/location)

### Dashboard
- `GET /api/dashboard/staff-presence` - Staff presence data

## Data Models

### Order
```javascript
{
  id: string,
  order_number: "ORD-0001",  // Sequential format
  customer_name: string,
  created_by: string,
  created_by_name: string,
  status: "pending" | "completed",
  created_at: datetime,
  items: [OrderItem]
}
```

### Product
```javascript
{
  // ... other fields
  selling_price: float,
  mrp: float,
  unit: "piece" | "meter" | "kg" | "box" | "set" | "roll" | "pack",
  gst_percentage: 0 | 5 | 12 | 18 | 28
}
```

## Key Files
- `frontend/src/pages/staff/CreateOrder.js` - Order ID input + Generate
- `frontend/src/pages/staff/PicklistPage.js` - QR + Print CSS
- `frontend/src/pages/public/CataloguePage.js` - Price display
- `frontend/src/pages/admin/AdminDashboard.js` - Staff Monitor
- `backend/server.py` - All API endpoints

## Prioritized Backlog

### Completed ✅
- All core features
- Mobile responsiveness
- Order ID sequence
- POS thermal print fix
- QR code plain text format
- Price in catalogue
- Staff presence system

### P1 (Pending)
- [ ] PDF download for picklists
- [ ] Barcode scanner hardware integration
- [ ] GST invoice generation

### P2 (Future)
- [ ] Bulk product import
- [ ] Multi-branch support
- [ ] Supplier purchase orders

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123

## Printer Settings for Thermal POS
- Paper Type: Roll Paper (NOT A4)
- Disable: "Print blank page"
- Disable: "Form feed"
- Disable: "Add margin"
- Page size: 80mm Roll
