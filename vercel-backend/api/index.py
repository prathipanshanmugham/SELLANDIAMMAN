from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import traceback

# Debug: Print Python version and environment info
print(f"Python version: {sys.version}", flush=True)
print(f"Starting Sellandiamman API...", flush=True)

try:
    import jwt
    print("jwt imported successfully", flush=True)
except ImportError as e:
    print(f"Error importing jwt: {e}", flush=True)
    jwt = None

try:
    import bcrypt
    print("bcrypt imported successfully", flush=True)
except ImportError as e:
    print(f"Error importing bcrypt: {e}", flush=True)
    bcrypt = None

try:
    import pymysql
    import pymysql.cursors
    print("pymysql imported successfully", flush=True)
except ImportError as e:
    print(f"Error importing pymysql: {e}", flush=True)
    pymysql = None

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

# MySQL Configuration
MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
MYSQL_USER = os.environ.get('MYSQL_USER', '')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', '')

print(f"MYSQL_HOST configured: {'Yes' if MYSQL_HOST else 'No'}", flush=True)
print(f"MYSQL_USER configured: {'Yes' if MYSQL_USER else 'No'}", flush=True)
print(f"MYSQL_DATABASE configured: {'Yes' if MYSQL_DATABASE else 'No'}", flush=True)

MYSQL_CONFIG = {
    'host': MYSQL_HOST,
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'db': MYSQL_DATABASE,
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor if pymysql else None
}

JWT_SECRET = os.environ.get('JWT_SECRET', 'sellandiamman-secret-2024')
JWT_ALGORITHM = "HS256"

def get_db():
    if not pymysql:
        raise Exception("pymysql not available")
    if not MYSQL_HOST or not MYSQL_USER or not MYSQL_DATABASE:
        raise Exception(f"Missing MySQL config: HOST={bool(MYSQL_HOST)}, USER={bool(MYSQL_USER)}, DB={bool(MYSQL_DATABASE)}")
    return pymysql.connect(**MYSQL_CONFIG)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id, email, role, name):
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "name": name,
        "exp": datetime.now(timezone.utc).timestamp() + 86400
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        return None

def generate_location_code(zone, aisle, rack, shelf, bin):
    return f"{zone}-{str(aisle).zfill(2)}-R{str(rack).zfill(2)}-S{shelf}-B{str(bin).zfill(2)}"

def cors_headers():
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
    
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def do_PATCH(self):
        self.handle_request('PATCH')
    
    def send_json(self, status, data):
        self.send_response(status)
        for key, value in cors_headers().items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def get_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length:
            return json.loads(self.rfile.read(content_length))
        return {}
    
    def get_user(self):
        auth = self.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            return verify_token(auth[7:])
        return None
    
    def handle_request(self, method):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        print(f"Handling {method} request for {path}", flush=True)
        
        try:
            # Health check
            if path == '/api/health':
                # Test database connection
                db_status = "unknown"
                db_error = None
                try:
                    if pymysql and MYSQL_HOST:
                        conn = get_db()
                        conn.close()
                        db_status = "connected"
                    else:
                        db_status = "not_configured"
                except Exception as db_e:
                    db_status = "error"
                    db_error = str(db_e)
                
                return self.send_json(200, {
                    "status": "healthy",
                    "database": db_status,
                    "db_error": db_error,
                    "python_version": sys.version,
                    "modules": {
                        "jwt": jwt is not None,
                        "bcrypt": bcrypt is not None,
                        "pymysql": pymysql is not None
                    },
                    "env_configured": {
                        "MYSQL_HOST": bool(MYSQL_HOST),
                        "MYSQL_USER": bool(MYSQL_USER),
                        "MYSQL_DATABASE": bool(MYSQL_DATABASE)
                    }
                })
            
            if path == '/api':
                return self.send_json(200, {"message": "Sellandiamman Traders API", "status": "running"})
            
            # Auth routes
            if path == '/api/auth/login' and method == 'POST':
                return self.handle_login()
            
            if path == '/api/auth/me' and method == 'GET':
                return self.handle_get_me()
            
            # Products routes
            if path == '/api/products' and method == 'GET':
                return self.handle_get_products(query)
            
            if path == '/api/products' and method == 'POST':
                return self.handle_create_product()
            
            if path.startswith('/api/products/') and method == 'GET':
                product_id = path.split('/')[-1]
                if product_id == 'categories':
                    return self.handle_get_categories()
                if product_id == 'zones':
                    return self.handle_get_zones()
                return self.handle_get_product(product_id)
            
            if path.startswith('/api/products/') and method == 'PUT':
                product_id = path.split('/')[-1]
                return self.handle_update_product(product_id)
            
            if path.startswith('/api/products/') and method == 'DELETE':
                product_id = path.split('/')[-1]
                return self.handle_delete_product(product_id)
            
            # Employees routes
            if path == '/api/employees' and method == 'GET':
                return self.handle_get_employees()
            
            if path == '/api/employees' and method == 'POST':
                return self.handle_create_employee()
            
            # Orders routes
            if path == '/api/orders' and method == 'GET':
                return self.handle_get_orders(query)
            
            if path == '/api/orders' and method == 'POST':
                return self.handle_create_order()
            
            if path == '/api/orders/next-order-id' and method == 'GET':
                return self.handle_next_order_id()
            
            if path.startswith('/api/orders/') and method == 'GET':
                order_id = path.split('/')[-1]
                return self.handle_get_order(order_id)
            
            # Dashboard routes
            if path == '/api/dashboard/stats' and method == 'GET':
                return self.handle_dashboard_stats()
            
            if path == '/api/dashboard/staff-presence' and method == 'GET':
                return self.handle_staff_presence()
            
            # Public routes
            if path == '/api/public/catalogue' and method == 'GET':
                return self.handle_public_catalogue(query)
            
            if path == '/api/public/categories' and method == 'GET':
                return self.handle_public_categories()
            
            return self.send_json(404, {"detail": "Not found"})
            
        except Exception as e:
            print(f"Error in handle_request: {str(e)}", flush=True)
            print(f"Traceback: {traceback.format_exc()}", flush=True)
            return self.send_json(500, {"detail": str(e), "traceback": traceback.format_exc()})
    
    # === AUTH HANDLERS ===
    def handle_login(self):
        body = self.get_body()
        email = body.get('email')
        password = body.get('password')
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employees WHERE email = %s", (email,))
                emp = cur.fetchone()
            
            if not emp:
                return self.send_json(401, {"detail": "Invalid credentials"})
            
            if not verify_password(password, emp.get("password_hash", "")):
                return self.send_json(401, {"detail": "Invalid credentials"})
            
            if emp.get("status") != "active":
                return self.send_json(401, {"detail": "Account is inactive"})
            
            token = create_token(emp["id"], emp["email"], emp["role"], emp["name"])
            
            return self.send_json(200, {
                "token": token,
                "user": {
                    "id": emp["id"],
                    "name": emp["name"],
                    "email": emp["email"],
                    "role": emp["role"],
                    "status": emp["status"],
                    "created_at": str(emp["created_at"])
                },
                "force_password_change": bool(emp.get("force_password_change", 0))
            })
        finally:
            conn.close()
    
    def handle_get_me(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employees WHERE id = %s", (user["user_id"],))
                emp = cur.fetchone()
            
            if not emp:
                return self.send_json(404, {"detail": "User not found"})
            
            return self.send_json(200, {
                "id": emp["id"],
                "name": emp["name"],
                "email": emp["email"],
                "role": emp["role"],
                "status": emp["status"],
                "created_at": str(emp["created_at"])
            })
        finally:
            conn.close()
    
    # === PRODUCT HANDLERS ===
    def handle_get_products(self, query):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            sql = "SELECT * FROM products ORDER BY product_name LIMIT 500"
            with conn.cursor() as cur:
                cur.execute(sql)
                products = cur.fetchall()
            
            result = [{
                "id": p["id"],
                "sku": p["sku"],
                "product_name": p["product_name"],
                "category": p["category"],
                "brand": p["brand"] or "",
                "zone": p["zone"],
                "aisle": p["aisle"],
                "rack": p["rack"],
                "shelf": p["shelf"],
                "bin": p["bin"],
                "full_location_code": p["full_location_code"],
                "quantity_available": p["quantity_available"],
                "reorder_level": p["reorder_level"],
                "supplier": p["supplier"] or "",
                "image_url": p["image_url"] or "",
                "selling_price": float(p["selling_price"] or 0),
                "mrp": float(p["mrp"] or 0),
                "unit": p["unit"] or "piece",
                "gst_percentage": float(p["gst_percentage"] or 18),
                "last_updated": str(p["last_updated"])
            } for p in products]
            
            return self.send_json(200, result)
        finally:
            conn.close()
    
    def handle_create_product(self):
        user = self.get_user()
        if not user or user.get("role") != "admin":
            return self.send_json(403, {"detail": "Admin access required"})
        
        body = self.get_body()
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM products WHERE sku = %s", (body["sku"],))
                if cur.fetchone():
                    return self.send_json(400, {"detail": "SKU already exists"})
            
            full_location = generate_location_code(
                body["zone"], body["aisle"], body["rack"], body["shelf"], body["bin"]
            )
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO products (sku, product_name, category, brand, zone, aisle, rack, shelf, bin,
                    full_location_code, quantity_available, reorder_level, supplier, image_url, selling_price,
                    mrp, unit, gst_percentage, last_updated, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    body["sku"], body["product_name"], body["category"], body.get("brand", ""),
                    body["zone"], body["aisle"], body["rack"], body["shelf"], body["bin"],
                    full_location, body.get("quantity_available", 0), body.get("reorder_level", 10),
                    body.get("supplier", ""), body.get("image_url", ""), body.get("selling_price", 0),
                    body.get("mrp", 0), body.get("unit", "piece"), body.get("gst_percentage", 18)
                ))
                prod_id = cur.lastrowid
            conn.commit()
            
            return self.send_json(201, {"id": prod_id, "message": "Product created"})
        finally:
            conn.close()
    
    def handle_get_product(self, product_id):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                p = cur.fetchone()
            
            if not p:
                return self.send_json(404, {"detail": "Product not found"})
            
            return self.send_json(200, {
                "id": p["id"],
                "sku": p["sku"],
                "product_name": p["product_name"],
                "category": p["category"],
                "brand": p["brand"] or "",
                "zone": p["zone"],
                "aisle": p["aisle"],
                "rack": p["rack"],
                "shelf": p["shelf"],
                "bin": p["bin"],
                "full_location_code": p["full_location_code"],
                "quantity_available": p["quantity_available"],
                "reorder_level": p["reorder_level"],
                "supplier": p["supplier"] or "",
                "image_url": p["image_url"] or "",
                "selling_price": float(p["selling_price"] or 0),
                "mrp": float(p["mrp"] or 0),
                "unit": p["unit"] or "piece",
                "gst_percentage": float(p["gst_percentage"] or 18),
                "last_updated": str(p["last_updated"])
            })
        finally:
            conn.close()
    
    def handle_update_product(self, product_id):
        user = self.get_user()
        if not user or user.get("role") != "admin":
            return self.send_json(403, {"detail": "Admin access required"})
        
        body = self.get_body()
        conn = get_db()
        try:
            full_location = generate_location_code(
                body["zone"], body["aisle"], body["rack"], body["shelf"], body["bin"]
            )
            
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE products SET sku=%s, product_name=%s, category=%s, brand=%s, zone=%s,
                    aisle=%s, rack=%s, shelf=%s, bin=%s, full_location_code=%s, quantity_available=%s,
                    reorder_level=%s, supplier=%s, image_url=%s, selling_price=%s, mrp=%s, unit=%s,
                    gst_percentage=%s, last_updated=NOW() WHERE id=%s
                """, (
                    body["sku"], body["product_name"], body["category"], body.get("brand", ""),
                    body["zone"], body["aisle"], body["rack"], body["shelf"], body["bin"],
                    full_location, body.get("quantity_available", 0), body.get("reorder_level", 10),
                    body.get("supplier", ""), body.get("image_url", ""), body.get("selling_price", 0),
                    body.get("mrp", 0), body.get("unit", "piece"), body.get("gst_percentage", 18),
                    product_id
                ))
            conn.commit()
            
            return self.send_json(200, {"message": "Product updated"})
        finally:
            conn.close()
    
    def handle_delete_product(self, product_id):
        user = self.get_user()
        if not user or user.get("role") != "admin":
            return self.send_json(403, {"detail": "Admin access required"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            return self.send_json(200, {"message": "Product deleted"})
        finally:
            conn.close()
    
    def handle_get_categories(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
                cats = cur.fetchall()
            return self.send_json(200, [c["category"] for c in cats if c["category"]])
        finally:
            conn.close()
    
    def handle_get_zones(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT zone FROM products WHERE zone IS NOT NULL ORDER BY zone")
                zones = cur.fetchall()
            return self.send_json(200, [z["zone"] for z in zones if z["zone"]])
        finally:
            conn.close()
    
    # === EMPLOYEE HANDLERS ===
    def handle_get_employees(self):
        user = self.get_user()
        if not user or user.get("role") != "admin":
            return self.send_json(403, {"detail": "Admin access required"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employees ORDER BY created_at DESC")
                employees = cur.fetchall()
            
            result = [{
                "id": e["id"],
                "name": e["name"],
                "email": e["email"],
                "role": e["role"],
                "status": e["status"],
                "presence_status": e.get("presence_status", "present"),
                "created_at": str(e["created_at"])
            } for e in employees]
            
            return self.send_json(200, result)
        finally:
            conn.close()
    
    def handle_create_employee(self):
        user = self.get_user()
        if not user or user.get("role") != "admin":
            return self.send_json(403, {"detail": "Admin access required"})
        
        body = self.get_body()
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM employees WHERE email = %s", (body["email"],))
                if cur.fetchone():
                    return self.send_json(400, {"detail": "Email already exists"})
                
                cur.execute("""
                    INSERT INTO employees (name, email, role, status, password_hash, presence_status, created_at)
                    VALUES (%s, %s, %s, 'active', %s, 'present', NOW())
                """, (body["name"], body["email"], body.get("role", "staff"), hash_password(body["password"])))
                emp_id = cur.lastrowid
            conn.commit()
            
            return self.send_json(201, {"id": emp_id, "message": "Employee created"})
        finally:
            conn.close()
    
    # === ORDER HANDLERS ===
    def handle_get_orders(self, query):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 100")
                orders = cur.fetchall()
            
            result = []
            for o in orders:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM order_items WHERE order_id = %s", (o["id"],))
                    items = cur.fetchall()
                
                result.append({
                    "id": o["id"],
                    "order_number": o["order_number"],
                    "customer_name": o["customer_name"],
                    "created_by": o["created_by"],
                    "created_by_name": o["created_by_name"],
                    "status": o["status"],
                    "created_at": str(o["created_at"]),
                    "items": [{
                        "id": i["id"],
                        "sku": i["sku"],
                        "product_name": i["product_name"],
                        "full_location_code": i["full_location_code"],
                        "quantity_required": i["quantity_required"],
                        "quantity_available": i["quantity_available"],
                        "picking_status": i["picking_status"]
                    } for i in items]
                })
            
            return self.send_json(200, result)
        finally:
            conn.close()
    
    def handle_next_order_id(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT order_number FROM orders WHERE order_number REGEXP '^ORD-[0-9]{4}$'
                    ORDER BY CAST(SUBSTRING(order_number, 5) AS UNSIGNED) DESC LIMIT 1
                """)
                result = cur.fetchone()
            
            if result:
                next_num = int(result["order_number"][4:]) + 1
            else:
                next_num = 1
            
            return self.send_json(200, {"next_order_id": f"ORD-{str(next_num).zfill(4)}"})
        finally:
            conn.close()
    
    def handle_create_order(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        body = self.get_body()
        conn = get_db()
        try:
            # Generate order number
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT order_number FROM orders WHERE order_number REGEXP '^ORD-[0-9]{4}$'
                    ORDER BY CAST(SUBSTRING(order_number, 5) AS UNSIGNED) DESC LIMIT 1
                """)
                result = cur.fetchone()
            
            if body.get("order_id"):
                order_number = body["order_id"].strip().upper()
            elif result:
                next_num = int(result["order_number"][4:]) + 1
                order_number = f"ORD-{str(next_num).zfill(4)}"
            else:
                order_number = "ORD-0001"
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO orders (order_number, customer_name, created_by, created_by_name, status, created_at)
                    VALUES (%s, %s, %s, %s, 'pending', NOW())
                """, (order_number, body["customer_name"], user["user_id"], user["name"]))
                order_id = cur.lastrowid
            
            for item in body.get("items", []):
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM products WHERE sku = %s", (item["sku"],))
                    product = cur.fetchone()
                
                if product:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO order_items (order_id, sku, product_name, full_location_code,
                            quantity_required, quantity_available, picking_status)
                            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
                        """, (
                            order_id, item["sku"], product["product_name"], product["full_location_code"],
                            item["quantity_required"], product["quantity_available"]
                        ))
            
            conn.commit()
            return self.send_json(201, {"id": order_id, "order_number": order_number})
        finally:
            conn.close()
    
    def handle_get_order(self, order_id):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
                o = cur.fetchone()
            
            if not o:
                return self.send_json(404, {"detail": "Order not found"})
            
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
                items = cur.fetchall()
            
            return self.send_json(200, {
                "id": o["id"],
                "order_number": o["order_number"],
                "customer_name": o["customer_name"],
                "created_by": o["created_by"],
                "created_by_name": o["created_by_name"],
                "status": o["status"],
                "created_at": str(o["created_at"]),
                "items": [{
                    "id": i["id"],
                    "sku": i["sku"],
                    "product_name": i["product_name"],
                    "full_location_code": i["full_location_code"],
                    "quantity_required": i["quantity_required"],
                    "quantity_available": i["quantity_available"],
                    "picking_status": i["picking_status"]
                } for i in items]
            })
        finally:
            conn.close()
    
    # === DASHBOARD HANDLERS ===
    def handle_dashboard_stats(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) as cnt FROM products")
                total_products = cur.fetchone()["cnt"]
                
                cur.execute("SELECT COALESCE(SUM(quantity_available), 0) as total FROM products")
                total_stock = int(cur.fetchone()["total"])
                
                cur.execute("SELECT COUNT(*) as cnt FROM products WHERE quantity_available <= reorder_level")
                low_stock = cur.fetchone()["cnt"]
                
                cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE DATE(created_at) = CURDATE()")
                sales_today = cur.fetchone()["cnt"]
                
                cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'pending'")
                orders_pending = cur.fetchone()["cnt"]
                
                cur.execute("SELECT COUNT(*) as cnt FROM orders WHERE status = 'completed'")
                orders_completed = cur.fetchone()["cnt"]
            
            return self.send_json(200, {
                "total_products": total_products,
                "total_stock_units": total_stock,
                "low_stock_items": low_stock,
                "sales_today": sales_today,
                "orders_pending": orders_pending,
                "orders_completed": orders_completed
            })
        finally:
            conn.close()
    
    def handle_staff_presence(self):
        user = self.get_user()
        if not user:
            return self.send_json(401, {"detail": "Not authenticated"})
        
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM employees")
                employees = cur.fetchall()
            
            result = [{
                "id": e["id"],
                "name": e["name"],
                "role": e["role"],
                "presence_status": e.get("presence_status", "present")
            } for e in employees]
            
            return self.send_json(200, result)
        finally:
            conn.close()
    
    # === PUBLIC HANDLERS ===
    def handle_public_catalogue(self, query):
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT sku, product_name, category, brand, image_url, selling_price, mrp, unit
                    FROM products ORDER BY product_name LIMIT 100
                """)
                products = cur.fetchall()
            
            result = [{
                "sku": p["sku"],
                "product_name": p["product_name"],
                "category": p["category"],
                "brand": p["brand"] or "",
                "image_url": p["image_url"] or "",
                "selling_price": float(p["selling_price"] or 0),
                "mrp": float(p["mrp"] or 0),
                "unit": p["unit"] or "piece"
            } for p in products]
            
            return self.send_json(200, result)
        finally:
            conn.close()
    
    def handle_public_categories(self):
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category")
                cats = cur.fetchall()
            return self.send_json(200, [c["category"] for c in cats if c["category"]])
        finally:
            conn.close()
