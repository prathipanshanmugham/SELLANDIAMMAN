from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'sellandiamman-traders-secret-key-2024')
JWT_ALGORITHM = "HS256"

# Create the main app
app = FastAPI(title="Sellandiamman Traders API")

# Create routers
api_router = APIRouter(prefix="/api")
auth_router = APIRouter(prefix="/api/auth", tags=["Authentication"])
products_router = APIRouter(prefix="/api/products", tags=["Products"])
employees_router = APIRouter(prefix="/api/employees", tags=["Employees"])
orders_router = APIRouter(prefix="/api/orders", tags=["Orders"])
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
public_router = APIRouter(prefix="/api/public", tags=["Public"])

security = HTTPBearer()

# ==================== MODELS ====================

class EmployeeBase(BaseModel):
    name: str
    email: EmailStr
    role: str = Field(..., pattern="^(admin|staff)$")

class EmployeeCreate(EmployeeBase):
    password: str

class Employee(EmployeeBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "active"
    presence_status: str = "present"  # present, permission, on_field, absent, on_leave
    presence_updated_at: Optional[str] = None
    presence_updated_by: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EmployeeResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    status: str
    presence_status: Optional[str] = "present"
    presence_updated_at: Optional[str] = None
    presence_updated_by: Optional[str] = None
    presence_updated_by_name: Optional[str] = None
    created_at: str

class PresenceStatusUpdate(BaseModel):
    presence_status: str = Field(..., pattern="^(present|permission|on_field|absent|on_leave)$")

class PresenceLogEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    employee_id: str
    employee_name: str
    previous_status: str
    new_status: str
    changed_by: str
    changed_by_name: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: EmployeeResponse

class ProductBase(BaseModel):
    sku: str
    product_name: str
    category: str
    brand: Optional[str] = ""
    zone: str
    aisle: int = Field(..., ge=1, le=99)
    rack: int = Field(..., ge=1, le=99)
    shelf: int = Field(..., ge=1, le=9)
    bin: int = Field(..., ge=1, le=99)
    quantity_available: int = Field(..., ge=0)
    reorder_level: int = Field(default=10, ge=0)
    supplier: Optional[str] = ""
    image_url: Optional[str] = ""
    selling_price: float = Field(default=0, ge=0)
    mrp: Optional[float] = Field(default=0, ge=0)
    unit: Optional[str] = "piece"  # piece, meter, kg, box, etc.
    gst_percentage: Optional[float] = Field(default=18, ge=0, le=100)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_location_code: str = ""
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProductResponse(BaseModel):
    id: str
    sku: str
    product_name: str
    category: str
    brand: str
    zone: str
    aisle: int
    rack: int
    shelf: int
    bin: int
    full_location_code: str
    quantity_available: int
    reorder_level: int
    supplier: str
    image_url: str
    selling_price: float = 0
    mrp: float = 0
    unit: str = "piece"
    gst_percentage: float = 18
    last_updated: str

class OrderItemBase(BaseModel):
    sku: str
    quantity_required: int = Field(..., ge=1)

class OrderItemResponse(BaseModel):
    id: str
    sku: str
    product_name: str
    full_location_code: str
    quantity_required: int
    quantity_available: int
    picking_status: str

class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemBase]
    order_id: Optional[str] = None  # Optional custom order ID

class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer_name: str
    created_by: str
    created_by_name: str
    status: str
    created_at: str
    items: List[OrderItemResponse]

# Order Modification Models
class OrderModificationLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    order_number: str
    modified_by: str
    modified_by_name: str
    modification_type: str  # add_item, remove_item, qty_change, status_change, customer_change
    field_changed: str
    old_value: str
    new_value: str
    reason: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OrderUpdateCustomer(BaseModel):
    customer_name: str
    reason: Optional[str] = None

class OrderUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(pending|completed)$")
    reason: Optional[str] = None

class OrderAddItem(BaseModel):
    sku: str
    quantity_required: int = Field(..., ge=1)
    reason: Optional[str] = None

class OrderRemoveItem(BaseModel):
    item_id: str
    reason: Optional[str] = None

class OrderUpdateItemQty(BaseModel):
    quantity_required: int = Field(..., ge=1)
    reason: Optional[str] = None

class StockTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sku: str
    change_type: str
    quantity_changed: int
    performed_by: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DashboardStats(BaseModel):
    total_products: int
    total_stock_units: int
    low_stock_items: int
    sales_today: int
    orders_pending: int
    orders_completed: int

class PublicProduct(BaseModel):
    sku: str
    product_name: str
    category: str
    brand: str
    image_url: str
    selling_price: float = 0
    mrp: float = 0
    unit: str = "piece"

# ==================== HELPER FUNCTIONS ====================

def generate_location_code(zone: str, aisle: int, rack: int, shelf: int, bin: int) -> str:
    """Generate full location code: {Zone}-{Aisle(2digit)}-R{Rack(2digit)}-S{Shelf}-B{Bin(2digit)}"""
    return f"{zone}-{str(aisle).zfill(2)}-R{str(rack).zfill(2)}-S{shelf}-B{str(bin).zfill(2)}"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str, name: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "name": name,
        "exp": datetime.now(timezone.utc).timestamp() + 86400  # 24 hours
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: dict = Depends(get_current_user)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ==================== AUTH ROUTES ====================

@auth_router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    employee = await db.employees.find_one({"email": request.email}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, employee.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if employee.get("status") != "active":
        raise HTTPException(status_code=401, detail="Account is inactive")
    
    token = create_token(employee["id"], employee["email"], employee["role"], employee["name"])
    
    return LoginResponse(
        token=token,
        user=EmployeeResponse(
            id=employee["id"],
            name=employee["name"],
            email=employee["email"],
            role=employee["role"],
            status=employee["status"],
            created_at=employee["created_at"]
        )
    )

@auth_router.get("/me", response_model=EmployeeResponse)
async def get_me(user: dict = Depends(get_current_user)):
    employee = await db.employees.find_one({"id": user["user_id"]}, {"_id": 0})
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    return EmployeeResponse(
        id=employee["id"],
        name=employee["name"],
        email=employee["email"],
        role=employee["role"],
        status=employee["status"],
        created_at=employee["created_at"]
    )

# ==================== EMPLOYEE ROUTES ====================

@employees_router.post("", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, user: dict = Depends(require_admin)):
    existing = await db.employees.find_one({"email": employee.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    emp_obj = Employee(
        name=employee.name,
        email=employee.email,
        role=employee.role
    )
    
    doc = emp_obj.model_dump()
    doc["password_hash"] = hash_password(employee.password)
    
    await db.employees.insert_one(doc)
    
    return EmployeeResponse(
        id=doc["id"],
        name=doc["name"],
        email=doc["email"],
        role=doc["role"],
        status=doc["status"],
        created_at=doc["created_at"]
    )

@employees_router.get("", response_model=List[EmployeeResponse])
async def get_employees(user: dict = Depends(require_admin)):
    employees = await db.employees.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    result = []
    for emp in employees:
        # Get the name of who updated presence
        presence_updated_by_name = None
        if emp.get("presence_updated_by"):
            updater = await db.employees.find_one({"id": emp["presence_updated_by"]}, {"_id": 0, "name": 1})
            if updater:
                presence_updated_by_name = updater.get("name")
        
        result.append(EmployeeResponse(
            id=emp["id"],
            name=emp["name"],
            email=emp["email"],
            role=emp["role"],
            status=emp["status"],
            presence_status=emp.get("presence_status", "present"),
            presence_updated_at=emp.get("presence_updated_at"),
            presence_updated_by=emp.get("presence_updated_by"),
            presence_updated_by_name=presence_updated_by_name,
            created_at=emp["created_at"]
        ))
    return result

@employees_router.get("/presence-log")
async def get_presence_log(limit: int = 50, user: dict = Depends(require_admin)):
    """Get presence status change history"""
    logs = await db.presence_logs.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit).to_list(limit)
    return logs

@employees_router.patch("/{employee_id}/presence")
async def update_presence_status(employee_id: str, update: PresenceStatusUpdate, user: dict = Depends(require_admin)):
    """Update staff presence status (admin only)"""
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    previous_status = employee.get("presence_status", "present")
    new_status = update.presence_status
    
    # Update employee presence
    await db.employees.update_one(
        {"id": employee_id},
        {"$set": {
            "presence_status": new_status,
            "presence_updated_at": datetime.now(timezone.utc).isoformat(),
            "presence_updated_by": user["user_id"]
        }}
    )
    
    # Log the change
    log_entry = PresenceLogEntry(
        employee_id=employee_id,
        employee_name=employee["name"],
        previous_status=previous_status,
        new_status=new_status,
        changed_by=user["user_id"],
        changed_by_name=user["name"]
    )
    await db.presence_logs.insert_one(log_entry.model_dump())
    
    return {"message": f"Presence status updated to {new_status}"}

@employees_router.delete("/{employee_id}")
async def delete_employee(employee_id: str, user: dict = Depends(require_admin)):
    if user["user_id"] == employee_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.employees.delete_one({"id": employee_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted"}

@employees_router.patch("/{employee_id}/status")
async def toggle_employee_status(employee_id: str, user: dict = Depends(require_admin)):
    employee = await db.employees.find_one({"id": employee_id})
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    new_status = "inactive" if employee["status"] == "active" else "active"
    await db.employees.update_one({"id": employee_id}, {"$set": {"status": new_status}})
    return {"message": f"Employee status changed to {new_status}"}

# ==================== PRODUCT ROUTES ====================

@products_router.post("", response_model=ProductResponse)
async def create_product(product: ProductCreate, user: dict = Depends(require_admin)):
    existing = await db.products.find_one({"sku": product.sku})
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    full_location_code = generate_location_code(
        product.zone, product.aisle, product.rack, product.shelf, product.bin
    )
    
    prod_obj = Product(
        **product.model_dump(),
        full_location_code=full_location_code
    )
    
    doc = prod_obj.model_dump()
    await db.products.insert_one(doc)
    
    return ProductResponse(**doc)

@products_router.get("", response_model=List[ProductResponse])
async def get_products(
    search: Optional[str] = None,
    category: Optional[str] = None,
    zone: Optional[str] = None,
    low_stock: Optional[bool] = None,
    limit: int = 100,
    skip: int = 0,
    user: dict = Depends(get_current_user)
):
    query = {}
    
    if search:
        query["$or"] = [
            {"sku": {"$regex": search, "$options": "i"}},
            {"product_name": {"$regex": search, "$options": "i"}},
            {"full_location_code": {"$regex": search, "$options": "i"}}
        ]
    
    if category:
        query["category"] = category
    
    if zone:
        query["zone"] = zone
    
    if low_stock:
        query["$expr"] = {"$lte": ["$quantity_available", "$reorder_level"]}
    
    products = await db.products.find(query, {"_id": 0}).skip(skip).limit(min(limit, 500)).to_list(min(limit, 500))
    return [ProductResponse(**prod) for prod in products]

@products_router.get("/categories")
async def get_categories(user: dict = Depends(get_current_user)):
    categories = await db.products.distinct("category")
    return categories

@products_router.get("/zones")
async def get_zones(user: dict = Depends(get_current_user)):
    zones = await db.products.distinct("zone")
    return zones

@products_router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, user: dict = Depends(get_current_user)):
    product = await db.products.find_one({"id": product_id}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product)

@products_router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product: ProductCreate, user: dict = Depends(require_admin)):
    existing = await db.products.find_one({"id": product_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    sku_check = await db.products.find_one({"sku": product.sku, "id": {"$ne": product_id}})
    if sku_check:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    full_location_code = generate_location_code(
        product.zone, product.aisle, product.rack, product.shelf, product.bin
    )
    
    update_data = product.model_dump()
    update_data["full_location_code"] = full_location_code
    update_data["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    await db.products.update_one({"id": product_id}, {"$set": update_data})
    
    updated = await db.products.find_one({"id": product_id}, {"_id": 0})
    return ProductResponse(**updated)

@products_router.delete("/{product_id}")
async def delete_product(product_id: str, user: dict = Depends(require_admin)):
    result = await db.products.delete_one({"id": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

@products_router.patch("/{product_id}/stock")
async def adjust_stock(
    product_id: str,
    quantity: int,
    reason: str = "manual_adjustment",
    user: dict = Depends(require_admin)
):
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_quantity = product["quantity_available"] + quantity
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {
            "quantity_available": new_quantity,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    transaction = StockTransaction(
        sku=product["sku"],
        change_type=reason,
        quantity_changed=quantity,
        performed_by=user["user_id"]
    )
    await db.stock_transactions.insert_one(transaction.model_dump())
    
    return {"message": "Stock adjusted", "new_quantity": new_quantity}

# ==================== ORDER ROUTES ====================

async def generate_next_order_number():
    """Generate next sequential order number: ORD-0001, ORD-0002, etc."""
    # Find the highest order number
    pipeline = [
        {"$match": {"order_number": {"$regex": "^ORD-\\d{4}$"}}},
        {"$project": {"num": {"$toInt": {"$substr": ["$order_number", 4, 4]}}}},
        {"$sort": {"num": -1}},
        {"$limit": 1}
    ]
    result = await db.orders.aggregate(pipeline).to_list(1)
    
    if result:
        next_num = result[0]["num"] + 1
    else:
        next_num = 1
    
    return f"ORD-{str(next_num).zfill(4)}"

@orders_router.get("/next-order-id")
async def get_next_order_id(user: dict = Depends(get_current_user)):
    """Get the next auto-generated order ID"""
    next_id = await generate_next_order_number()
    return {"next_order_id": next_id}

@orders_router.post("", response_model=OrderResponse)
async def create_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    # Use custom order_id if provided, otherwise auto-generate
    if order.order_id and order.order_id.strip():
        # Check if custom order ID already exists
        existing = await db.orders.find_one({"order_number": order.order_id})
        if existing:
            raise HTTPException(status_code=400, detail=f"Order ID {order.order_id} already exists")
        order_number = order.order_id.strip().upper()
    else:
        order_number = await generate_next_order_number()
    
    order_items = []
    for item in order.items:
        product = await db.products.find_one({"sku": item.sku}, {"_id": 0})
        if not product:
            raise HTTPException(status_code=400, detail=f"Product with SKU {item.sku} not found")
        
        order_items.append({
            "id": str(uuid.uuid4()),
            "sku": item.sku,
            "product_name": product["product_name"],
            "full_location_code": product["full_location_code"],
            "quantity_required": item.quantity_required,
            "quantity_available": product["quantity_available"],
            "picking_status": "pending"
        })
    
    order_doc = {
        "id": str(uuid.uuid4()),
        "order_number": order_number,
        "customer_name": order.customer_name,
        "created_by": user["user_id"],
        "created_by_name": user["name"],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "items": order_items
    }
    
    await db.orders.insert_one(order_doc)
    
    return OrderResponse(**order_doc)

@orders_router.get("", response_model=List[OrderResponse])
async def get_orders(
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
    user: dict = Depends(get_current_user)
):
    query = {}
    if status:
        query["status"] = status
    
    orders = await db.orders.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(min(limit, 200)).to_list(min(limit, 200))
    return [OrderResponse(**order) for order in orders]

@orders_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, user: dict = Depends(get_current_user)):
    order = await db.orders.find_one({"id": order_id}, {"_id": 0})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(**order)

@orders_router.patch("/{order_id}/items/{item_id}/pick")
async def mark_item_picked(order_id: str, item_id: str, user: dict = Depends(get_current_user)):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item = None
    for i in order["items"]:
        if i["id"] == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["picking_status"] == "picked":
        raise HTTPException(status_code=400, detail="Item already picked")
    
    # Deduct stock
    product = await db.products.find_one({"sku": item["sku"]})
    if product:
        new_quantity = product["quantity_available"] - item["quantity_required"]
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        await db.products.update_one(
            {"sku": item["sku"]},
            {"$set": {
                "quantity_available": new_quantity,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Log transaction
        transaction = StockTransaction(
            sku=item["sku"],
            change_type="sale",
            quantity_changed=-item["quantity_required"],
            performed_by=user["user_id"]
        )
        await db.stock_transactions.insert_one(transaction.model_dump())
    
    # Update item status
    await db.orders.update_one(
        {"id": order_id, "items.id": item_id},
        {"$set": {"items.$.picking_status": "picked"}}
    )
    
    # Check if all items picked
    updated_order = await db.orders.find_one({"id": order_id})
    all_picked = all(i["picking_status"] == "picked" for i in updated_order["items"])
    
    if all_picked:
        await db.orders.update_one({"id": order_id}, {"$set": {"status": "completed"}})
    
    return {"message": "Item marked as picked", "stock_deducted": item["quantity_required"]}

# ==================== ORDER MODIFICATION ROUTES ====================

async def log_order_modification(order_id: str, order_number: str, user: dict, 
                                  mod_type: str, field: str, old_val: str, new_val: str, reason: str = None):
    """Helper function to log order modifications"""
    log_entry = OrderModificationLog(
        order_id=order_id,
        order_number=order_number,
        modified_by=user["user_id"],
        modified_by_name=user["name"],
        modification_type=mod_type,
        field_changed=field,
        old_value=old_val,
        new_value=new_val,
        reason=reason
    )
    await db.order_modification_logs.insert_one(log_entry.model_dump())

@orders_router.get("/{order_id}/modification-history")
async def get_order_modification_history(order_id: str, user: dict = Depends(get_current_user)):
    """Get modification history for an order"""
    logs = await db.order_modification_logs.find(
        {"order_id": order_id}, 
        {"_id": 0}
    ).sort("timestamp", -1).to_list(100)
    return logs

@orders_router.patch("/{order_id}/customer")
async def update_order_customer(order_id: str, update: OrderUpdateCustomer, user: dict = Depends(get_current_user)):
    """Update customer name - staff can only edit pending orders"""
    # Validate customer name
    if not update.customer_name or not update.customer_name.strip():
        raise HTTPException(status_code=400, detail="Customer name cannot be empty")
    
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Permission check
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    old_value = order["customer_name"]
    new_value = update.customer_name.strip()
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"customer_name": new_value}}
    )
    
    # Log modification
    await log_order_modification(
        order_id, order["order_number"], user,
        "customer_change", "customer_name",
        old_value, new_value, update.reason
    )
    
    return {"message": "Customer name updated", "old_value": old_value, "new_value": new_value}

@orders_router.patch("/{order_id}/status")
async def update_order_status(order_id: str, update: OrderUpdateStatus, user: dict = Depends(require_admin)):
    """Update order status - Admin only (can reopen completed orders)"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order["status"]
    
    await db.orders.update_one(
        {"id": order_id},
        {"$set": {"status": update.status}}
    )
    
    # Log modification
    await log_order_modification(
        order_id, order["order_number"], user,
        "status_change", "status",
        old_status, update.status, update.reason
    )
    
    return {"message": f"Order status changed from {old_status} to {update.status}"}

@orders_router.post("/{order_id}/items")
async def add_order_item(order_id: str, item: OrderAddItem, user: dict = Depends(get_current_user)):
    """Add item to existing order"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Permission check
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    # Get product details
    product = await db.products.find_one({"sku": item.sku}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=400, detail=f"Product with SKU {item.sku} not found")
    
    # Check if item already exists
    for existing_item in order["items"]:
        if existing_item["sku"] == item.sku:
            raise HTTPException(status_code=400, detail=f"Item {item.sku} already exists. Use quantity update instead.")
    
    new_item = {
        "id": str(uuid.uuid4()),
        "sku": item.sku,
        "product_name": product["product_name"],
        "full_location_code": product["full_location_code"],
        "quantity_required": item.quantity_required,
        "quantity_available": product["quantity_available"],
        "picking_status": "pending"
    }
    
    await db.orders.update_one(
        {"id": order_id},
        {"$push": {"items": new_item}, "$set": {"status": "pending"}}
    )
    
    # Log modification
    await log_order_modification(
        order_id, order["order_number"], user,
        "add_item", "items",
        "", f"{item.sku} x{item.quantity_required}", item.reason
    )
    
    return {"message": f"Item {item.sku} added", "item_id": new_item["id"]}

@orders_router.delete("/{order_id}/items/{item_id}")
async def remove_order_item(order_id: str, item_id: str, reason: Optional[str] = None, user: dict = Depends(get_current_user)):
    """Remove item from order"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Permission check
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    # Find the item
    item_to_remove = None
    for item in order["items"]:
        if item["id"] == item_id:
            item_to_remove = item
            break
    
    if not item_to_remove:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # If item was picked, reverse the stock deduction
    if item_to_remove["picking_status"] == "picked":
        product = await db.products.find_one({"sku": item_to_remove["sku"]})
        if product:
            new_quantity = product["quantity_available"] + item_to_remove["quantity_required"]
            await db.products.update_one(
                {"sku": item_to_remove["sku"]},
                {"$set": {
                    "quantity_available": new_quantity,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            # Log stock reversal
            transaction = StockTransaction(
                sku=item_to_remove["sku"],
                change_type="reversal_remove_item",
                quantity_changed=item_to_remove["quantity_required"],
                performed_by=user["user_id"]
            )
            await db.stock_transactions.insert_one(transaction.model_dump())
    
    # Remove the item
    await db.orders.update_one(
        {"id": order_id},
        {"$pull": {"items": {"id": item_id}}}
    )
    
    # Log modification
    await log_order_modification(
        order_id, order["order_number"], user,
        "remove_item", "items",
        f"{item_to_remove['sku']} x{item_to_remove['quantity_required']}", "", reason
    )
    
    return {"message": f"Item {item_to_remove['sku']} removed", "stock_restored": item_to_remove["quantity_required"] if item_to_remove["picking_status"] == "picked" else 0}

@orders_router.patch("/{order_id}/items/{item_id}/quantity")
async def update_item_quantity(order_id: str, item_id: str, update: OrderUpdateItemQty, user: dict = Depends(get_current_user)):
    """Update item quantity"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Permission check
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    # Find the item
    item = None
    for i in order["items"]:
        if i["id"] == item_id:
            item = i
            break
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    old_qty = item["quantity_required"]
    new_qty = update.quantity_required
    qty_diff = new_qty - old_qty
    
    # If item was picked, adjust stock
    if item["picking_status"] == "picked":
        product = await db.products.find_one({"sku": item["sku"]})
        if product:
            # Reverse old deduction and apply new
            adjusted_quantity = product["quantity_available"] - qty_diff
            if adjusted_quantity < 0:
                raise HTTPException(status_code=400, detail="Insufficient stock for quantity increase")
            
            await db.products.update_one(
                {"sku": item["sku"]},
                {"$set": {
                    "quantity_available": adjusted_quantity,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }}
            )
            # Log stock adjustment
            transaction = StockTransaction(
                sku=item["sku"],
                change_type="qty_adjustment",
                quantity_changed=-qty_diff,
                performed_by=user["user_id"]
            )
            await db.stock_transactions.insert_one(transaction.model_dump())
    
    # Update the quantity
    await db.orders.update_one(
        {"id": order_id, "items.id": item_id},
        {"$set": {"items.$.quantity_required": new_qty}}
    )
    
    # Log modification
    await log_order_modification(
        order_id, order["order_number"], user,
        "qty_change", f"quantity ({item['sku']})",
        str(old_qty), str(new_qty), update.reason
    )
    
    return {"message": f"Quantity updated from {old_qty} to {new_qty}", "stock_adjusted": qty_diff if item["picking_status"] == "picked" else 0}

@orders_router.delete("/{order_id}")
async def delete_order(order_id: str, reason: Optional[str] = None, user: dict = Depends(require_admin)):
    """Delete order - Admin only with logging"""
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Log the deletion before deleting
    await log_order_modification(
        order_id, order["order_number"], user,
        "delete_order", "order",
        f"Order {order['order_number']} with {len(order['items'])} items", "DELETED", reason
    )
    
    # Reverse any picked item stock deductions
    for item in order["items"]:
        if item["picking_status"] == "picked":
            product = await db.products.find_one({"sku": item["sku"]})
            if product:
                new_quantity = product["quantity_available"] + item["quantity_required"]
                await db.products.update_one(
                    {"sku": item["sku"]},
                    {"$set": {
                        "quantity_available": new_quantity,
                        "last_updated": datetime.now(timezone.utc).isoformat()
                    }}
                )
                # Log stock reversal
                transaction = StockTransaction(
                    sku=item["sku"],
                    change_type="reversal_order_delete",
                    quantity_changed=item["quantity_required"],
                    performed_by=user["user_id"]
                )
                await db.stock_transactions.insert_one(transaction.model_dump())
    
    await db.orders.delete_one({"id": order_id})
    return {"message": "Order deleted", "order_number": order["order_number"]}

# ==================== DASHBOARD ROUTES ====================

@dashboard_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    total_products = await db.products.count_documents({})
    
    pipeline = [{"$group": {"_id": None, "total": {"$sum": "$quantity_available"}}}]
    stock_result = await db.products.aggregate(pipeline).to_list(1)
    total_stock = stock_result[0]["total"] if stock_result else 0
    
    low_stock_pipeline = [
        {"$match": {"$expr": {"$lte": ["$quantity_available", "$reorder_level"]}}},
        {"$count": "count"}
    ]
    low_stock_result = await db.products.aggregate(low_stock_pipeline).to_list(1)
    low_stock_count = low_stock_result[0]["count"] if low_stock_result else 0
    
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sales_today = await db.orders.count_documents({
        "created_at": {"$regex": f"^{today}"}
    })
    
    orders_pending = await db.orders.count_documents({"status": "pending"})
    orders_completed = await db.orders.count_documents({"status": "completed"})
    
    return DashboardStats(
        total_products=total_products,
        total_stock_units=total_stock,
        low_stock_items=low_stock_count,
        sales_today=sales_today,
        orders_pending=orders_pending,
        orders_completed=orders_completed
    )

@dashboard_router.get("/zone-distribution")
async def get_zone_distribution(user: dict = Depends(get_current_user)):
    pipeline = [
        {"$group": {"_id": "$zone", "count": {"$sum": 1}, "stock": {"$sum": "$quantity_available"}}},
        {"$project": {"zone": "$_id", "count": 1, "stock": 1, "_id": 0}}
    ]
    result = await db.products.aggregate(pipeline).to_list(100)
    return result

@dashboard_router.get("/category-distribution")
async def get_category_distribution(user: dict = Depends(get_current_user)):
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$project": {"category": "$_id", "count": 1, "_id": 0}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    result = await db.products.aggregate(pipeline).to_list(10)
    return result

@dashboard_router.get("/recent-transactions")
async def get_recent_transactions(user: dict = Depends(get_current_user)):
    transactions = await db.stock_transactions.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).to_list(20)
    return transactions

@dashboard_router.get("/low-stock-items")
async def get_low_stock_items(user: dict = Depends(get_current_user)):
    pipeline = [
        {"$match": {"$expr": {"$lte": ["$quantity_available", "$reorder_level"]}}},
        {"$project": {
            "_id": 0,
            "sku": 1,
            "product_name": 1,
            "quantity_available": 1,
            "reorder_level": 1,
            "full_location_code": 1
        }},
        {"$limit": 20}
    ]
    result = await db.products.aggregate(pipeline).to_list(20)
    return result

@dashboard_router.get("/staff-presence")
async def get_staff_presence(user: dict = Depends(get_current_user)):
    """Get all staff presence status for dashboard"""
    employees = await db.employees.find({}, {"_id": 0, "password_hash": 0}).to_list(100)
    result = []
    for emp in employees:
        # Get the name of who updated presence
        presence_updated_by_name = None
        if emp.get("presence_updated_by"):
            updater = await db.employees.find_one({"id": emp["presence_updated_by"]}, {"_id": 0, "name": 1})
            if updater:
                presence_updated_by_name = updater.get("name")
        
        result.append({
            "id": emp["id"],
            "name": emp["name"],
            "role": emp["role"],
            "presence_status": emp.get("presence_status", "present"),
            "presence_updated_at": emp.get("presence_updated_at"),
            "presence_updated_by_name": presence_updated_by_name
        })
    return result

# ==================== PUBLIC ROUTES (NO AUTH) ====================

@public_router.get("/catalogue", response_model=List[PublicProduct])
async def get_public_catalogue(
    search: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    query = {}
    if search:
        query["$or"] = [
            {"sku": {"$regex": search, "$options": "i"}},
            {"product_name": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = category
    
    # Only return public fields - NO stock info, NO location
    products = await db.products.find(
        query,
        {"_id": 0, "sku": 1, "product_name": 1, "category": 1, "brand": 1, "image_url": 1, 
         "selling_price": 1, "mrp": 1, "unit": 1}
    ).skip(skip).limit(min(limit, 100)).to_list(min(limit, 100))
    
    return [PublicProduct(**prod) for prod in products]

@public_router.get("/categories")
async def get_public_categories():
    categories = await db.products.distinct("category")
    return categories

# ==================== ROOT & HEALTH ====================

@api_router.get("/")
async def root():
    return {"message": "Sellandiamman Traders API", "status": "running"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_db():
    # Create default admin if not exists
    admin = await db.employees.find_one({"email": "admin@sellandiamman.com"})
    if not admin:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "name": "Admin",
            "email": "admin@sellandiamman.com",
            "role": "admin",
            "status": "active",
            "password_hash": hash_password("admin123"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.employees.insert_one(admin_doc)
        logging.info("Default admin created: admin@sellandiamman.com / admin123")
    
    # Create indexes
    await db.products.create_index("sku", unique=True)
    await db.products.create_index("full_location_code")
    await db.employees.create_index("email", unique=True)
    await db.orders.create_index("order_number", unique=True)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Include all routers
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(employees_router)
app.include_router(orders_router)
app.include_router(dashboard_router)
app.include_router(public_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
