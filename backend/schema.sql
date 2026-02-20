-- Sellandiamman Traders MySQL Schema
-- Database: u217264814_Sellandiamman

-- Employees Table
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'staff') NOT NULL DEFAULT 'staff',
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    presence_status ENUM('present', 'permission', 'on_field', 'absent', 'on_leave') DEFAULT 'present',
    presence_updated_at DATETIME NULL,
    presence_updated_by INT NULL,
    force_password_change TINYINT(1) DEFAULT 0,
    security_question VARCHAR(255) NULL,
    security_answer_hash VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),
    zone VARCHAR(10),
    aisle INT,
    rack INT,
    shelf INT,
    bin INT,
    full_location_code VARCHAR(50),
    quantity_available INT DEFAULT 0,
    reorder_level INT DEFAULT 10,
    supplier VARCHAR(100),
    image_url VARCHAR(500),
    selling_price DECIMAL(10,2) DEFAULT 0,
    mrp DECIMAL(10,2) DEFAULT 0,
    unit VARCHAR(20) DEFAULT 'piece',
    gst_percentage DECIMAL(5,2) DEFAULT 18,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_category (category),
    INDEX idx_zone (zone),
    INDEX idx_location (full_location_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_name VARCHAR(150) NOT NULL,
    created_by INT NOT NULL,
    created_by_name VARCHAR(100),
    status ENUM('pending', 'completed') DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_number (order_number),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    sku VARCHAR(50) NOT NULL,
    product_name VARCHAR(255),
    full_location_code VARCHAR(50),
    quantity_required INT NOT NULL,
    quantity_available INT DEFAULT 0,
    picking_status ENUM('pending', 'picked') DEFAULT 'pending',
    INDEX idx_order_id (order_id),
    INDEX idx_sku (sku),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Order Modification Logs Table
CREATE TABLE IF NOT EXISTS order_modification_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    order_number VARCHAR(50),
    modified_by INT NOT NULL,
    modified_by_name VARCHAR(100),
    modification_type VARCHAR(50),
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_order_id (order_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Stock Transactions Table
CREATE TABLE IF NOT EXISTS stock_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku VARCHAR(50) NOT NULL,
    change_type VARCHAR(50),
    quantity_changed INT,
    performed_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_sku (sku),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Presence Logs Table
CREATE TABLE IF NOT EXISTS presence_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    employee_name VARCHAR(100),
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    changed_by INT,
    changed_by_name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_employee_id (employee_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
