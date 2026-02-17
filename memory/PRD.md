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

## What's Been Implemented

### Feb 17, 2026 - New Features
**1. Master QR Barcode on Receipts**
- QR code added to Picklist page containing JSON data
- Format: `{order_id, customer, items: [{sku, qty}]}`
- Scannable by external billing software (Odoo, Zoho, etc.)
- Shows "Scan to Auto Load Bill" text
- Visible on both screen and thermal print

**2. Staff Live Presence System**
- Admin can set staff status: Present (🟢), Permission (🟡), On Field (🔵), Absent (🔴), On Leave (⚫)
- "Staff Live Monitor" panel on Admin Dashboard
- Real-time status updates with dropdown selector
- Status change history logged to `presence_logs` collection
- Staff cannot change their own presence (admin-only)

### Feb 16, 2026 - Mobile Responsiveness
- Shared `PublicNavbar` component with hamburger menu
- Mobile card views for Products, Orders, Staff pages
- Enhanced Admin Dashboard with 2-column grid stats
- All pages tested at 375px viewport

### Feb 15, 2026 - Core Features
- Complete backend API
- Public pages with SEO
- WhatsApp floating button
- Thermal receipt print layout

## Backend API Endpoints

### Authentication
- `POST /api/auth/login` - JWT login
- `GET /api/auth/me` - Get current user

### Employees
- `GET /api/employees` - List all (admin only)
- `POST /api/employees` - Create staff (admin only)
- `DELETE /api/employees/{id}` - Delete staff (admin only)
- `PATCH /api/employees/{id}/status` - Toggle active/inactive
- `PATCH /api/employees/{id}/presence` - Update presence status (admin only)
- `GET /api/employees/presence-log` - Get status change history (admin only)

### Products
- `GET /api/products` - List with filters
- `POST /api/products` - Create product (admin only)
- `GET /api/products/{id}` - Get single product
- `PUT /api/products/{id}` - Update product (admin only)
- `DELETE /api/products/{id}` - Delete product (admin only)
- `PATCH /api/products/{id}/stock` - Adjust stock (admin only)
- `GET /api/products/categories` - List categories
- `GET /api/products/zones` - List zones

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - List orders
- `GET /api/orders/{id}` - Get order details
- `PATCH /api/orders/{id}/items/{item_id}/pick` - Mark item picked (deducts stock)
- `DELETE /api/orders/{id}` - Delete order (admin only)

### Dashboard
- `GET /api/dashboard/stats` - Dashboard statistics
- `GET /api/dashboard/zone-distribution` - Zone chart data
- `GET /api/dashboard/category-distribution` - Category chart data
- `GET /api/dashboard/low-stock-items` - Low stock alerts
- `GET /api/dashboard/staff-presence` - Staff presence data
- `GET /api/dashboard/recent-transactions` - Recent stock transactions

### Public (No Auth)
- `GET /api/public/catalogue` - Product list (no stock info)
- `GET /api/public/categories` - Category list

## Data Models

### Employee
```javascript
{
  id: string,
  name: string,
  email: string,
  role: "admin" | "staff",
  status: "active" | "inactive",
  presence_status: "present" | "permission" | "on_field" | "absent" | "on_leave",
  presence_updated_at: datetime,
  presence_updated_by: string,
  password_hash: string,
  created_at: datetime
}
```

### Presence Log
```javascript
{
  id: string,
  employee_id: string,
  employee_name: string,
  previous_status: string,
  new_status: string,
  changed_by: string,
  changed_by_name: string,
  timestamp: datetime
}
```

### QR Code Data Format
```json
{
  "order_id": "ORD-20260217-0001",
  "customer": "Customer Name",
  "items": [
    {"sku": "WIRE001", "qty": 5},
    {"sku": "MCB001", "qty": 2}
  ]
}
```

## Key Files
- `frontend/src/pages/staff/PicklistPage.js` - QR code implementation
- `frontend/src/pages/admin/AdminDashboard.js` - Staff Live Monitor panel
- `frontend/src/components/common/PublicNavbar.js` - Mobile navigation
- `backend/server.py` - All API endpoints

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] Authentication system
- [x] Product CRUD with location codes
- [x] Order creation workflow
- [x] Pick and stock deduction
- [x] Mobile responsiveness
- [x] Master QR Barcode
- [x] Staff Presence System

### P1 (Important) - Pending
- [ ] PDF download for picklists
- [ ] Barcode scanner integration
- [ ] GST invoice generation

### P2 (Nice to Have)
- [ ] Bulk product import
- [ ] Multi-branch support
- [ ] Supplier purchase orders
- [ ] Stock history reports

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123

## Location Code Format
`{Zone}-{Aisle(2digit)}-R{Rack(2digit)}-S{Shelf}-B{Bin(2digit)}`
Example: `A-03-R07-S2-B05`
