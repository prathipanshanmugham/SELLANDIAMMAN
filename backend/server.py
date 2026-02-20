from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi import status as http_status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import jwt
import bcrypt
import aiomysql

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MySQL Configuration
MYSQL_CONFIG = {
    'host': os.environ['MYSQL_HOST'],
    'user': os.environ['MYSQL_USER'],
    'password': os.environ['MYSQL_PASSWORD'],
    'db': os.environ['MYSQL_DATABASE'],
    'autocommit': True,
    'charset': 'utf8mb4'
}

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'sellandiamman-traders-secret-key-2024')
JWT_ALGORITHM = "HS256"

# Database pool
pool = None

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

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    presence_status: Optional[str] = "present"
    presence_updated_at: Optional[str] = None
    presence_updated_by: Optional[int] = None
    presence_updated_by_name: Optional[str] = None
    force_password_change: bool = False
    has_security_question: bool = False
    created_at: str

class PresenceStatusUpdate(BaseModel):
    presence_status: str = Field(..., pattern="^(present|permission|on_field|absent|on_leave)$")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    token: str
    user: EmployeeResponse
    force_password_change: bool = False

class ResetStaffPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)
    force_change_on_login: bool = False

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class SetSecurityQuestionRequest(BaseModel):
    security_question: str
    security_answer: str = Field(..., min_length=2)
    current_password: str

class AdminResetPasswordRequest(BaseModel):
    email: EmailStr
    security_answer: str
    new_password: str = Field(..., min_length=6)

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
    unit: Optional[str] = "piece"
    gst_percentage: Optional[float] = Field(default=18, ge=0, le=100)

class ProductCreate(ProductBase):
    pass

class ProductResponse(BaseModel):
    id: int
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
    id: int
    sku: str
    product_name: str
    full_location_code: str
    quantity_required: int
    quantity_available: int
    picking_status: str

class OrderCreate(BaseModel):
    customer_name: str
    items: List[OrderItemBase]
    order_id: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    created_by: int
    created_by_name: str
    status: str
    created_at: str
    items: List[OrderItemResponse]

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

class OrderUpdateItemQty(BaseModel):
    quantity_required: int = Field(..., ge=1)
    reason: Optional[str] = None

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
    return f"{zone}-{str(aisle).zfill(2)}-R{str(rack).zfill(2)}-S{shelf}-B{str(bin).zfill(2)}"

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: int, email: str, role: str, name: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "name": name,
        "exp": datetime.now(timezone.utc).timestamp() + 86400
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_db():
    global pool
    if pool is None:
        pool = await aiomysql.create_pool(**MYSQL_CONFIG)
    return pool

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
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM employees WHERE email = %s",
                (request.email,)
            )
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(request.password, employee.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if employee.get("status") != "active":
        raise HTTPException(status_code=401, detail="Account is inactive")
    
    token = create_token(employee["id"], employee["email"], employee["role"], employee["name"])
    force_password_change = bool(employee.get("force_password_change", 0))
    
    return LoginResponse(
        token=token,
        user=EmployeeResponse(
            id=employee["id"],
            name=employee["name"],
            email=employee["email"],
            role=employee["role"],
            status=employee["status"],
            force_password_change=force_password_change,
            has_security_question=bool(employee.get("security_question")),
            created_at=str(employee["created_at"])
        ),
        force_password_change=force_password_change
    )

@auth_router.get("/me", response_model=EmployeeResponse)
async def get_me(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE id = %s", (user["user_id"],))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    
    return EmployeeResponse(
        id=employee["id"],
        name=employee["name"],
        email=employee["email"],
        role=employee["role"],
        status=employee["status"],
        force_password_change=bool(employee.get("force_password_change", 0)),
        has_security_question=bool(employee.get("security_question")),
        created_at=str(employee["created_at"])
    )

@auth_router.post("/change-password")
async def change_own_password(request: ChangePasswordRequest, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE id = %s", (user["user_id"],))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(request.current_password, employee.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE employees SET password_hash = %s, force_password_change = 0 WHERE id = %s",
                (hash_password(request.new_password), user["user_id"])
            )
    
    return {"message": "Password changed successfully"}

@auth_router.post("/set-security-question")
async def set_security_question(request: SetSecurityQuestionRequest, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE id = %s", (user["user_id"],))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not verify_password(request.current_password, employee.get("password_hash", "")):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE employees SET security_question = %s, security_answer_hash = %s WHERE id = %s",
                (request.security_question, hash_password(request.security_answer.lower().strip()), user["user_id"])
            )
    
    return {"message": "Security question set successfully"}

@auth_router.get("/security-question/{email}")
async def get_security_question(email: str):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE email = %s", (email,))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    
    if employee.get("role") != "admin":
        raise HTTPException(status_code=400, detail="Security question reset is only for admin accounts")
    
    security_question = employee.get("security_question")
    if not security_question:
        raise HTTPException(status_code=400, detail="No security question set. Contact system administrator.")
    
    return {"security_question": security_question}

@auth_router.post("/reset-password-with-security")
async def reset_password_with_security(request: AdminResetPasswordRequest):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE email = %s", (request.email,))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="User not found")
    
    if employee.get("role") != "admin":
        raise HTTPException(status_code=400, detail="This reset method is only for admin accounts")
    
    security_answer_hash = employee.get("security_answer_hash")
    if not security_answer_hash:
        raise HTTPException(status_code=400, detail="No security question set")
    
    if not verify_password(request.security_answer.lower().strip(), security_answer_hash):
        raise HTTPException(status_code=401, detail="Incorrect security answer")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE employees SET password_hash = %s, force_password_change = 0 WHERE email = %s",
                (hash_password(request.new_password), request.email)
            )
    
    return {"message": "Password reset successfully. You can now login."}

# ==================== EMPLOYEE ROUTES ====================

@employees_router.post("", response_model=EmployeeResponse)
async def create_employee(employee: EmployeeCreate, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM employees WHERE email = %s", (employee.email,))
            existing = await cur.fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO employees (name, email, role, status, password_hash, presence_status, created_at) 
                   VALUES (%s, %s, %s, 'active', %s, 'present', NOW())""",
                (employee.name, employee.email, employee.role, hash_password(employee.password))
            )
            emp_id = cur.lastrowid
    
    return EmployeeResponse(
        id=emp_id,
        name=employee.name,
        email=employee.email,
        role=employee.role,
        status="active",
        created_at=datetime.now(timezone.utc).isoformat()
    )

@employees_router.get("", response_model=List[EmployeeResponse])
async def get_employees(user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees ORDER BY created_at DESC")
            employees = await cur.fetchall()
    
    result = []
    for emp in employees:
        presence_updated_by_name = None
        if emp.get("presence_updated_by"):
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute("SELECT name FROM employees WHERE id = %s", (emp["presence_updated_by"],))
                    updater = await cur.fetchone()
                    if updater:
                        presence_updated_by_name = updater.get("name")
        
        result.append(EmployeeResponse(
            id=emp["id"],
            name=emp["name"],
            email=emp["email"],
            role=emp["role"],
            status=emp["status"],
            presence_status=emp.get("presence_status", "present"),
            presence_updated_at=str(emp["presence_updated_at"]) if emp.get("presence_updated_at") else None,
            presence_updated_by=emp.get("presence_updated_by"),
            presence_updated_by_name=presence_updated_by_name,
            force_password_change=bool(emp.get("force_password_change", 0)),
            has_security_question=bool(emp.get("security_question")),
            created_at=str(emp["created_at"])
        ))
    return result

@employees_router.get("/presence-log")
async def get_presence_log(limit: int = 50, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM presence_logs ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
            logs = await cur.fetchall()
    return [dict(log) for log in logs]

@employees_router.patch("/{employee_id}/presence")
async def update_presence_status(employee_id: int, update: PresenceStatusUpdate, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    previous_status = employee.get("presence_status", "present")
    new_status = update.presence_status
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """UPDATE employees SET presence_status = %s, presence_updated_at = NOW(), 
                   presence_updated_by = %s WHERE id = %s""",
                (new_status, user["user_id"], employee_id)
            )
            await cur.execute(
                """INSERT INTO presence_logs (employee_id, employee_name, previous_status, new_status, 
                   changed_by, changed_by_name, created_at) VALUES (%s, %s, %s, %s, %s, %s, NOW())""",
                (employee_id, employee["name"], previous_status, new_status, user["user_id"], user["name"])
            )
    
    return {"message": f"Presence status updated to {new_status}"}

@employees_router.delete("/{employee_id}")
async def delete_employee(employee_id: int, user: dict = Depends(require_admin)):
    if user["user_id"] == employee_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            result = await cur.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
    
    if result == 0:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted"}

@employees_router.patch("/{employee_id}/status")
async def toggle_employee_status(employee_id: int, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT status FROM employees WHERE id = %s", (employee_id,))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    new_status = "inactive" if employee["status"] == "active" else "active"
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE employees SET status = %s WHERE id = %s", (new_status, employee_id))
    
    return {"message": f"Employee status changed to {new_status}"}

@employees_router.post("/{employee_id}/reset-password")
async def reset_staff_password(employee_id: int, request: ResetStaffPasswordRequest, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
            employee = await cur.fetchone()
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.get("role") == "admin" and employee["id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Cannot reset another admin's password. Use security question reset.")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE employees SET password_hash = %s, force_password_change = %s WHERE id = %s",
                (hash_password(request.new_password), 1 if request.force_change_on_login else 0, employee_id)
            )
    
    return {"message": f"Password reset for {employee['name']}", "force_change_on_login": request.force_change_on_login}

# ==================== PRODUCT ROUTES ====================

@products_router.post("", response_model=ProductResponse)
async def create_product(product: ProductCreate, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM products WHERE sku = %s", (product.sku,))
            existing = await cur.fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    full_location_code = generate_location_code(product.zone, product.aisle, product.rack, product.shelf, product.bin)
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO products (sku, product_name, category, brand, zone, aisle, rack, shelf, bin, 
                   full_location_code, quantity_available, reorder_level, supplier, image_url, selling_price, 
                   mrp, unit, gst_percentage, last_updated, created_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (product.sku, product.product_name, product.category, product.brand or "", product.zone,
                 product.aisle, product.rack, product.shelf, product.bin, full_location_code,
                 product.quantity_available, product.reorder_level, product.supplier or "", 
                 product.image_url or "", product.selling_price, product.mrp or 0, 
                 product.unit or "piece", product.gst_percentage or 18)
            )
            prod_id = cur.lastrowid
    
    return ProductResponse(
        id=prod_id, sku=product.sku, product_name=product.product_name, category=product.category,
        brand=product.brand or "", zone=product.zone, aisle=product.aisle, rack=product.rack,
        shelf=product.shelf, bin=product.bin, full_location_code=full_location_code,
        quantity_available=product.quantity_available, reorder_level=product.reorder_level,
        supplier=product.supplier or "", image_url=product.image_url or "", 
        selling_price=product.selling_price, mrp=product.mrp or 0, unit=product.unit or "piece",
        gst_percentage=product.gst_percentage or 18, last_updated=datetime.now(timezone.utc).isoformat()
    )

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
    db = await get_db()
    query = "SELECT * FROM products WHERE 1=1"
    params = []
    
    if search:
        query += " AND (sku LIKE %s OR product_name LIKE %s OR full_location_code LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param, search_param])
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    if zone:
        query += " AND zone = %s"
        params.append(zone)
    
    if low_stock:
        query += " AND quantity_available <= reorder_level"
    
    query += f" ORDER BY product_name LIMIT {min(limit, 500)} OFFSET {skip}"
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            products = await cur.fetchall()
    
    return [ProductResponse(
        id=p["id"], sku=p["sku"], product_name=p["product_name"], category=p["category"],
        brand=p["brand"] or "", zone=p["zone"], aisle=p["aisle"], rack=p["rack"],
        shelf=p["shelf"], bin=p["bin"], full_location_code=p["full_location_code"],
        quantity_available=p["quantity_available"], reorder_level=p["reorder_level"],
        supplier=p["supplier"] or "", image_url=p["image_url"] or "",
        selling_price=float(p["selling_price"] or 0), mrp=float(p["mrp"] or 0),
        unit=p["unit"] or "piece", gst_percentage=float(p["gst_percentage"] or 18),
        last_updated=str(p["last_updated"])
    ) for p in products]

@products_router.get("/categories")
async def get_categories(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
            categories = await cur.fetchall()
    return [c[0] for c in categories if c[0]]

@products_router.get("/zones")
async def get_zones(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT zone FROM products ORDER BY zone")
            zones = await cur.fetchall()
    return [z[0] for z in zones if z[0]]

@products_router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            p = await cur.fetchone()
    
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ProductResponse(
        id=p["id"], sku=p["sku"], product_name=p["product_name"], category=p["category"],
        brand=p["brand"] or "", zone=p["zone"], aisle=p["aisle"], rack=p["rack"],
        shelf=p["shelf"], bin=p["bin"], full_location_code=p["full_location_code"],
        quantity_available=p["quantity_available"], reorder_level=p["reorder_level"],
        supplier=p["supplier"] or "", image_url=p["image_url"] or "",
        selling_price=float(p["selling_price"] or 0), mrp=float(p["mrp"] or 0),
        unit=p["unit"] or "piece", gst_percentage=float(p["gst_percentage"] or 18),
        last_updated=str(p["last_updated"])
    )

@products_router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductCreate, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM products WHERE id = %s", (product_id,))
            existing = await cur.fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM products WHERE sku = %s AND id != %s", (product.sku, product_id))
            sku_check = await cur.fetchone()
    
    if sku_check:
        raise HTTPException(status_code=400, detail="SKU already exists")
    
    full_location_code = generate_location_code(product.zone, product.aisle, product.rack, product.shelf, product.bin)
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """UPDATE products SET sku=%s, product_name=%s, category=%s, brand=%s, zone=%s, 
                   aisle=%s, rack=%s, shelf=%s, bin=%s, full_location_code=%s, quantity_available=%s,
                   reorder_level=%s, supplier=%s, image_url=%s, selling_price=%s, mrp=%s, unit=%s,
                   gst_percentage=%s, last_updated=NOW() WHERE id=%s""",
                (product.sku, product.product_name, product.category, product.brand or "", product.zone,
                 product.aisle, product.rack, product.shelf, product.bin, full_location_code,
                 product.quantity_available, product.reorder_level, product.supplier or "",
                 product.image_url or "", product.selling_price, product.mrp or 0,
                 product.unit or "piece", product.gst_percentage or 18, product_id)
            )
    
    return ProductResponse(
        id=product_id, sku=product.sku, product_name=product.product_name, category=product.category,
        brand=product.brand or "", zone=product.zone, aisle=product.aisle, rack=product.rack,
        shelf=product.shelf, bin=product.bin, full_location_code=full_location_code,
        quantity_available=product.quantity_available, reorder_level=product.reorder_level,
        supplier=product.supplier or "", image_url=product.image_url or "",
        selling_price=product.selling_price, mrp=product.mrp or 0, unit=product.unit or "piece",
        gst_percentage=product.gst_percentage or 18, last_updated=datetime.now(timezone.utc).isoformat()
    )

@products_router.delete("/{product_id}")
async def delete_product(product_id: int, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            result = await cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    
    if result == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted"}

@products_router.patch("/{product_id}/stock")
async def adjust_stock(product_id: int, quantity: int, reason: str = "manual_adjustment", user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = await cur.fetchone()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    new_quantity = product["quantity_available"] + quantity
    if new_quantity < 0:
        raise HTTPException(status_code=400, detail="Stock cannot be negative")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE products SET quantity_available = %s, last_updated = NOW() WHERE id = %s",
                (new_quantity, product_id)
            )
            await cur.execute(
                """INSERT INTO stock_transactions (sku, change_type, quantity_changed, performed_by, created_at) 
                   VALUES (%s, %s, %s, %s, NOW())""",
                (product["sku"], reason, quantity, user["user_id"])
            )
    
    return {"message": "Stock adjusted", "new_quantity": new_quantity}

# ==================== ORDER ROUTES ====================

async def generate_next_order_number():
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT order_number FROM orders WHERE order_number REGEXP '^ORD-[0-9]{4}$' 
                   ORDER BY CAST(SUBSTRING(order_number, 5) AS UNSIGNED) DESC LIMIT 1"""
            )
            result = await cur.fetchone()
    
    if result:
        next_num = int(result[0][4:]) + 1
    else:
        next_num = 1
    
    return f"ORD-{str(next_num).zfill(4)}"

@orders_router.get("/next-order-id")
async def get_next_order_id(user: dict = Depends(get_current_user)):
    next_id = await generate_next_order_number()
    return {"next_order_id": next_id}

@orders_router.post("", response_model=OrderResponse)
async def create_order(order: OrderCreate, user: dict = Depends(get_current_user)):
    db = await get_db()
    
    if order.order_id and order.order_id.strip():
        async with db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT id FROM orders WHERE order_number = %s", (order.order_id,))
                existing = await cur.fetchone()
        if existing:
            raise HTTPException(status_code=400, detail=f"Order ID {order.order_id} already exists")
        order_number = order.order_id.strip().upper()
    else:
        order_number = await generate_next_order_number()
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO orders (order_number, customer_name, created_by, created_by_name, status, created_at) 
                   VALUES (%s, %s, %s, %s, 'pending', NOW())""",
                (order_number, order.customer_name, user["user_id"], user["name"])
            )
            order_id = cur.lastrowid
    
    order_items = []
    for item in order.items:
        async with db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM products WHERE sku = %s", (item.sku,))
                product = await cur.fetchone()
        
        if not product:
            raise HTTPException(status_code=400, detail=f"Product with SKU {item.sku} not found")
        
        async with db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """INSERT INTO order_items (order_id, sku, product_name, full_location_code, 
                       quantity_required, quantity_available, picking_status) 
                       VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
                    (order_id, item.sku, product["product_name"], product["full_location_code"],
                     item.quantity_required, product["quantity_available"])
                )
                item_id = cur.lastrowid
        
        order_items.append(OrderItemResponse(
            id=item_id, sku=item.sku, product_name=product["product_name"],
            full_location_code=product["full_location_code"], quantity_required=item.quantity_required,
            quantity_available=product["quantity_available"], picking_status="pending"
        ))
    
    return OrderResponse(
        id=order_id, order_number=order_number, customer_name=order.customer_name,
        created_by=user["user_id"], created_by_name=user["name"], status="pending",
        created_at=datetime.now(timezone.utc).isoformat(), items=order_items
    )

@orders_router.get("", response_model=List[OrderResponse])
async def get_orders(status: Optional[str] = None, limit: int = 50, skip: int = 0, user: dict = Depends(get_current_user)):
    db = await get_db()
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += f" ORDER BY created_at DESC LIMIT {min(limit, 200)} OFFSET {skip}"
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            orders = await cur.fetchall()
    
    result = []
    for o in orders:
        async with db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM order_items WHERE order_id = %s", (o["id"],))
                items = await cur.fetchall()
        
        result.append(OrderResponse(
            id=o["id"], order_number=o["order_number"], customer_name=o["customer_name"],
            created_by=o["created_by"], created_by_name=o["created_by_name"], status=o["status"],
            created_at=str(o["created_at"]),
            items=[OrderItemResponse(
                id=i["id"], sku=i["sku"], product_name=i["product_name"],
                full_location_code=i["full_location_code"], quantity_required=i["quantity_required"],
                quantity_available=i["quantity_available"], picking_status=i["picking_status"]
            ) for i in items]
        ))
    
    return result

@orders_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            o = await cur.fetchone()
    
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
            items = await cur.fetchall()
    
    return OrderResponse(
        id=o["id"], order_number=o["order_number"], customer_name=o["customer_name"],
        created_by=o["created_by"], created_by_name=o["created_by_name"], status=o["status"],
        created_at=str(o["created_at"]),
        items=[OrderItemResponse(
            id=i["id"], sku=i["sku"], product_name=i["product_name"],
            full_location_code=i["full_location_code"], quantity_required=i["quantity_required"],
            quantity_available=i["quantity_available"], picking_status=i["picking_status"]
        ) for i in items]
    )

@orders_router.patch("/{order_id}/items/{item_id}/pick")
async def mark_item_picked(order_id: int, item_id: int, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM order_items WHERE id = %s AND order_id = %s", (item_id, order_id))
            item = await cur.fetchone()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if item["picking_status"] == "picked":
        raise HTTPException(status_code=400, detail="Item already picked")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM products WHERE sku = %s", (item["sku"],))
            product = await cur.fetchone()
    
    if product:
        new_quantity = product["quantity_available"] - item["quantity_required"]
        if new_quantity < 0:
            raise HTTPException(status_code=400, detail="Insufficient stock")
        
        async with db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE products SET quantity_available = %s, last_updated = NOW() WHERE sku = %s",
                    (new_quantity, item["sku"])
                )
                await cur.execute(
                    """INSERT INTO stock_transactions (sku, change_type, quantity_changed, performed_by, created_at) 
                       VALUES (%s, 'sale', %s, %s, NOW())""",
                    (item["sku"], -item["quantity_required"], user["user_id"])
                )
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE order_items SET picking_status = 'picked' WHERE id = %s", (item_id,))
            
            await cur.execute(
                "SELECT COUNT(*) FROM order_items WHERE order_id = %s AND picking_status != 'picked'",
                (order_id,)
            )
            unpicked = (await cur.fetchone())[0]
            
            if unpicked == 0:
                await cur.execute("UPDATE orders SET status = 'completed' WHERE id = %s", (order_id,))
    
    return {"message": "Item marked as picked", "stock_deducted": item["quantity_required"]}

@orders_router.get("/{order_id}/modification-history")
async def get_order_modification_history(order_id: int, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM order_modification_logs WHERE order_id = %s ORDER BY created_at DESC",
                (order_id,)
            )
            logs = await cur.fetchall()
    return [dict(log) for log in logs]

@orders_router.patch("/{order_id}/customer")
async def update_order_customer(order_id: int, update: OrderUpdateCustomer, user: dict = Depends(get_current_user)):
    if not update.customer_name or not update.customer_name.strip():
        raise HTTPException(status_code=400, detail="Customer name cannot be empty")
    
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    old_value = order["customer_name"]
    new_value = update.customer_name.strip()
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE orders SET customer_name = %s WHERE id = %s", (new_value, order_id))
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'customer_change', 'customer_name', %s, %s, %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"], old_value, new_value, update.reason)
            )
    
    return {"message": "Customer name updated", "old_value": old_value, "new_value": new_value}

@orders_router.patch("/{order_id}/status")
async def update_order_status(order_id: int, update: OrderUpdateStatus, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    old_status = order["status"]
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE orders SET status = %s WHERE id = %s", (update.status, order_id))
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'status_change', 'status', %s, %s, %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"], old_status, update.status, update.reason)
            )
    
    return {"message": f"Order status changed from {old_status} to {update.status}"}

@orders_router.post("/{order_id}/items")
async def add_order_item(order_id: int, item: OrderAddItem, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM products WHERE sku = %s", (item.sku,))
            product = await cur.fetchone()
    
    if not product:
        raise HTTPException(status_code=400, detail=f"Product with SKU {item.sku} not found")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id FROM order_items WHERE order_id = %s AND sku = %s", (order_id, item.sku))
            existing = await cur.fetchone()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Item {item.sku} already exists. Use quantity update instead.")
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO order_items (order_id, sku, product_name, full_location_code, 
                   quantity_required, quantity_available, picking_status) 
                   VALUES (%s, %s, %s, %s, %s, %s, 'pending')""",
                (order_id, item.sku, product["product_name"], product["full_location_code"],
                 item.quantity_required, product["quantity_available"])
            )
            item_id = cur.lastrowid
            await cur.execute("UPDATE orders SET status = 'pending' WHERE id = %s", (order_id,))
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'add_item', 'items', '', %s, %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"], 
                 f"{item.sku} x{item.quantity_required}", item.reason)
            )
    
    return {"message": f"Item {item.sku} added", "item_id": item_id}

@orders_router.delete("/{order_id}/items/{item_id}")
async def remove_order_item(order_id: int, item_id: int, reason: Optional[str] = None, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM order_items WHERE id = %s AND order_id = %s", (item_id, order_id))
            item = await cur.fetchone()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stock_restored = 0
    if item["picking_status"] == "picked":
        async with db.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "UPDATE products SET quantity_available = quantity_available + %s, last_updated = NOW() WHERE sku = %s",
                    (item["quantity_required"], item["sku"])
                )
                await cur.execute(
                    """INSERT INTO stock_transactions (sku, change_type, quantity_changed, performed_by, created_at) 
                       VALUES (%s, 'reversal_remove_item', %s, %s, NOW())""",
                    (item["sku"], item["quantity_required"], user["user_id"])
                )
        stock_restored = item["quantity_required"]
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM order_items WHERE id = %s", (item_id,))
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'remove_item', 'items', %s, '', %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"],
                 f"{item['sku']} x{item['quantity_required']}", reason)
            )
    
    return {"message": f"Item {item['sku']} removed", "stock_restored": stock_restored}

@orders_router.patch("/{order_id}/items/{item_id}/quantity")
async def update_item_quantity(order_id: int, item_id: int, update: OrderUpdateItemQty, user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if user["role"] != "admin" and order["status"] == "completed":
        raise HTTPException(status_code=403, detail="Staff cannot edit completed orders")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM order_items WHERE id = %s AND order_id = %s", (item_id, order_id))
            item = await cur.fetchone()
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    old_qty = item["quantity_required"]
    new_qty = update.quantity_required
    qty_diff = new_qty - old_qty
    stock_adjusted = 0
    
    if item["picking_status"] == "picked":
        async with db.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT quantity_available FROM products WHERE sku = %s", (item["sku"],))
                product = await cur.fetchone()
        
        if product:
            adjusted_quantity = product["quantity_available"] - qty_diff
            if adjusted_quantity < 0:
                raise HTTPException(status_code=400, detail="Insufficient stock for quantity increase")
            
            async with db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE products SET quantity_available = %s, last_updated = NOW() WHERE sku = %s",
                        (adjusted_quantity, item["sku"])
                    )
                    await cur.execute(
                        """INSERT INTO stock_transactions (sku, change_type, quantity_changed, performed_by, created_at) 
                           VALUES (%s, 'qty_adjustment', %s, %s, NOW())""",
                        (item["sku"], -qty_diff, user["user_id"])
                    )
            stock_adjusted = qty_diff
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE order_items SET quantity_required = %s WHERE id = %s", (new_qty, item_id))
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'qty_change', %s, %s, %s, %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"],
                 f"quantity ({item['sku']})", str(old_qty), str(new_qty), update.reason)
            )
    
    return {"message": f"Quantity updated from {old_qty} to {new_qty}", "stock_adjusted": stock_adjusted}

@orders_router.delete("/{order_id}")
async def delete_order(order_id: int, reason: Optional[str] = None, user: dict = Depends(require_admin)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            order = await cur.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
            items = await cur.fetchall()
    
    for item in items:
        if item["picking_status"] == "picked":
            async with db.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "UPDATE products SET quantity_available = quantity_available + %s, last_updated = NOW() WHERE sku = %s",
                        (item["quantity_required"], item["sku"])
                    )
                    await cur.execute(
                        """INSERT INTO stock_transactions (sku, change_type, quantity_changed, performed_by, created_at) 
                           VALUES (%s, 'reversal_order_delete', %s, %s, NOW())""",
                        (item["sku"], item["quantity_required"], user["user_id"])
                    )
    
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO order_modification_logs (order_id, order_number, modified_by, modified_by_name,
                   modification_type, field_changed, old_value, new_value, reason, created_at)
                   VALUES (%s, %s, %s, %s, 'delete_order', 'order', %s, 'DELETED', %s, NOW())""",
                (order_id, order["order_number"], user["user_id"], user["name"],
                 f"Order {order['order_number']} with {len(items)} items", reason)
            )
            await cur.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
            await cur.execute("DELETE FROM orders WHERE id = %s", (order_id,))
    
    return {"message": "Order deleted", "order_number": order["order_number"]}

# ==================== DASHBOARD ROUTES ====================

@dashboard_router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM products")
            total_products = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COALESCE(SUM(quantity_available), 0) FROM products")
            total_stock = int((await cur.fetchone())[0])
            
            await cur.execute("SELECT COUNT(*) FROM products WHERE quantity_available <= reorder_level")
            low_stock_count = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE()")
            sales_today = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
            orders_pending = (await cur.fetchone())[0]
            
            await cur.execute("SELECT COUNT(*) FROM orders WHERE status = 'completed'")
            orders_completed = (await cur.fetchone())[0]
    
    return DashboardStats(
        total_products=total_products, total_stock_units=total_stock, low_stock_items=low_stock_count,
        sales_today=sales_today, orders_pending=orders_pending, orders_completed=orders_completed
    )

@dashboard_router.get("/zone-distribution")
async def get_zone_distribution(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT zone, COUNT(*) as count, SUM(quantity_available) as stock FROM products GROUP BY zone"
            )
            result = await cur.fetchall()
    return [dict(r) for r in result]

@dashboard_router.get("/category-distribution")
async def get_category_distribution(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT category, COUNT(*) as count FROM products GROUP BY category ORDER BY count DESC LIMIT 10"
            )
            result = await cur.fetchall()
    return [dict(r) for r in result]

@dashboard_router.get("/recent-transactions")
async def get_recent_transactions(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM stock_transactions ORDER BY created_at DESC LIMIT 20")
            transactions = await cur.fetchall()
    return [dict(t) for t in transactions]

@dashboard_router.get("/low-stock-items")
async def get_low_stock_items(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """SELECT sku, product_name, quantity_available, reorder_level, full_location_code 
                   FROM products WHERE quantity_available <= reorder_level LIMIT 20"""
            )
            result = await cur.fetchall()
    return [dict(r) for r in result]

@dashboard_router.get("/staff-presence")
async def get_staff_presence(user: dict = Depends(get_current_user)):
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM employees")
            employees = await cur.fetchall()
    
    result = []
    for emp in employees:
        presence_updated_by_name = None
        if emp.get("presence_updated_by"):
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute("SELECT name FROM employees WHERE id = %s", (emp["presence_updated_by"],))
                    updater = await cur.fetchone()
                    if updater:
                        presence_updated_by_name = updater.get("name")
        
        result.append({
            "id": emp["id"],
            "name": emp["name"],
            "role": emp["role"],
            "presence_status": emp.get("presence_status", "present"),
            "presence_updated_at": str(emp["presence_updated_at"]) if emp.get("presence_updated_at") else None,
            "presence_updated_by_name": presence_updated_by_name
        })
    return result

# ==================== PUBLIC ROUTES (NO AUTH) ====================

@public_router.get("/catalogue", response_model=List[PublicProduct])
async def get_public_catalogue(search: Optional[str] = None, category: Optional[str] = None, limit: int = 50, skip: int = 0):
    db = await get_db()
    query = "SELECT sku, product_name, category, brand, image_url, selling_price, mrp, unit FROM products WHERE 1=1"
    params = []
    
    if search:
        query += " AND (sku LIKE %s OR product_name LIKE %s)"
        search_param = f"%{search}%"
        params.extend([search_param, search_param])
    
    if category:
        query += " AND category = %s"
        params.append(category)
    
    query += f" ORDER BY product_name LIMIT {min(limit, 100)} OFFSET {skip}"
    
    async with db.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            products = await cur.fetchall()
    
    return [PublicProduct(
        sku=p["sku"], product_name=p["product_name"], category=p["category"],
        brand=p["brand"] or "", image_url=p["image_url"] or "",
        selling_price=float(p["selling_price"] or 0), mrp=float(p["mrp"] or 0),
        unit=p["unit"] or "piece"
    ) for p in products]

@public_router.get("/categories")
async def get_public_categories():
    db = await get_db()
    async with db.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
            categories = await cur.fetchall()
    return [c[0] for c in categories if c[0]]

# ==================== ROOT & HEALTH ====================

@api_router.get("/")
async def root():
    return {"message": "Sellandiamman Traders API", "status": "running", "database": "MySQL"}

@api_router.get("/health")
async def health():
    return {"status": "healthy"}

# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_db():
    global pool
    try:
        pool = await aiomysql.create_pool(**MYSQL_CONFIG)
        logging.info("MySQL connection pool created")
        
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute("SELECT * FROM employees WHERE email = 'admin@sellandiamman.com'")
                admin = await cur.fetchone()
        
        if not admin:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """INSERT INTO employees (name, email, role, status, password_hash, presence_status, created_at) 
                           VALUES ('Admin', 'admin@sellandiamman.com', 'admin', 'active', %s, 'present', NOW())""",
                        (hash_password("admin123"),)
                    )
            logging.info("Default admin created: admin@sellandiamman.com / admin123")
        
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
