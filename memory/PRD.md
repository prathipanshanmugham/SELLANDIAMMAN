# Sellandiamman Traders - Inventory & Sales Management System

## Original Problem Statement
Build a private inventory + sales + picking management system for Sellandiamman Traders (Electrical Retail & Wholesale Store) with 10,000+ products capacity.

## Architecture
- **Frontend**: React + Tailwind CSS + Shadcn/UI + Recharts + react-barcode
- **Backend**: FastAPI + Motor (async MongoDB)
- **Database**: MongoDB
- **Authentication**: JWT-based (Admin/Staff roles)

## Latest Updates

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

**Audit Log Entry Structure:**
```javascript
{
  id: string,
  order_id: string,
  order_number: string,
  modified_by: string,
  modified_by_name: string,
  modification_type: "add_item" | "remove_item" | "qty_change" | "status_change" | "customer_change",
  field_changed: string,
  old_value: string,
  new_value: string,
  reason: string (optional),
  timestamp: datetime
}
```

**Stock Adjustment Logic:**
- If picked item removed → Stock restored
- If picked item qty decreased → Stock restored
- If picked item qty increased → Stock deducted
- All stock changes logged to `stock_transactions`

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

## API Endpoints

### Order Modification
```
GET  /api/orders/{id}/modification-history  - Get all modifications
PATCH /api/orders/{id}/customer             - Update customer name
PATCH /api/orders/{id}/status               - Update status (admin)
POST  /api/orders/{id}/items                - Add item
DELETE /api/orders/{id}/items/{item_id}     - Remove item
PATCH /api/orders/{id}/items/{item_id}/quantity - Update quantity
```

### Other Endpoints
- `/api/auth/login` - JWT login
- `/api/products` - Full CRUD
- `/api/orders` - Create, list, get
- `/api/dashboard` - Stats, charts, presence

## Frontend Pages

### /orders/:id/modify (OrderModify.js)
- **Modify Tab:** Edit customer, items, status
- **History Tab:** Timeline view of all changes
- Features:
  - Edit customer name with reason
  - Edit item quantity with reason
  - Add/remove items
  - Admin: Mark Complete / Reopen Order

## Database Collections
- `products` - Product catalog
- `employees` - Staff with presence status
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
- **Order modification with audit logging**

## Pending Features
- [ ] PDF download for picklists
- [ ] GST invoice generation
- [ ] Bulk product import

## Test Credentials
- **Admin**: admin@sellandiamman.com / admin123
