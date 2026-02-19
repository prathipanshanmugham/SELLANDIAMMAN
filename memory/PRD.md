# Sellandiamman Traders - Inventory & Sales Management System

## Original Problem Statement
Build a private inventory + sales + picking management system for Sellandiamman Traders (Electrical Retail & Wholesale Store) with 10,000+ products capacity.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + react-barcode
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Authentication**: JWT-based (Admin/Staff roles)

## Latest Updates

### Feb 19, 2026 - Security Enhancements

**1. Login Page Security:**
- Admin credentials no longer displayed on login page
- Generic placeholders ("Enter your email", "Enter your password")
- "Contact your administrator for login credentials" message
- "Admin forgot password?" link for password recovery

**2. Staff Password Management (Admin):**
- Reset staff passwords via Staff Management page
- Option to "Require password change on next login"
- Visual "Pwd Reset Required" badge for users with forced password change
- Admins cannot reset other admin passwords via this method

**3. Admin Password Recovery:**
- Security question system for admin accounts
- Set/update security question via Settings page
- Reset password by answering security question (no email required)
- Security answers are case-insensitive and hashed

**New API Endpoints:**
```
POST /api/employees/{id}/reset-password  - Admin resets staff password
POST /api/auth/change-password           - User changes own password
POST /api/auth/set-security-question     - Admin sets security question
GET  /api/auth/security-question/{email} - Get security question for admin
POST /api/auth/reset-password-with-security - Reset admin password
```

**New Frontend Pages:**
- `/admin/settings` - Account settings & security question
- `/forgot-password` - Admin password recovery flow
- `/change-password` - Forced password change page

### Feb 18, 2026 - Order Modification with Audit Logging

**Complete Order Modification System:**
- Edit orders after creation with full accountability
- Every change logged to `order_modification_logs` collection
- Admin sees full modification history
- Staff cannot secretly edit records

**Permission Rules:**
| Action | Staff | Admin |
|--------|-------|-------|
| Edit pending orders | ✅ | ✅ |
| Edit completed orders | ❌ | ✅ |
| Reopen completed orders | ❌ | ✅ |
| Delete orders | ❌ | ✅ |
| View history | ✅ | ✅ |

**What Can Be Modified:**
- ✅ Add item
- ✅ Remove item
- ✅ Change quantity
- ✅ Change customer name
- ✅ Change order status
- ❌ Change order ID

### Item-Level SKU Barcodes
- Code128 barcode per item (not master QR)
- Barcode value = SKU only
- Compatible with all POS systems

### Order ID System
- Format: ORD-0001 (4-digit sequence)
- Auto-generate or manual entry

### Price in Catalogue
- Public shows price (₹85/meter)
- Stock/location hidden

## Database Collections
- `products` - Product catalog
- `employees` - Staff with presence status, security questions
- `orders` - Orders with items
- `order_modification_logs` - Audit trail
- `stock_transactions` - Stock movement history
- `presence_logs` - Staff presence history

## Completed Features ✅
- Core inventory management
- Order creation workflow
- Pick and stock deduction
- Mobile responsiveness
- Order ID sequence
- Item-level SKU barcodes
- Price in catalogue
- Staff presence system
- Order modification with audit logging
- **Security enhancements (credentials hidden, password management, recovery)**

## Pending Features
- [ ] PDF download for picklists
- [ ] GST invoice generation
- [ ] Bulk product import

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123
- **Security Question Answer**: buddy
