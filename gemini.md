# 🧩 Microservices Django System - Requirement

## 🎯 1. Overview

Build a **microservices-based system using Django** with:

- Multiple independent services
- API Gateway for routing
- Separate UI for staff and customer
- Dockerized deployment
- Central orchestration via docker-compose

---

## 🧱 2. Architecture

Client
↓
API Gateway
↓
| staff-service (MySQL) |
| customer-service (MySQL) |
| cart-service (PostgreSQL) |
| laptop-service (PostgreSQL) |
| clothes-service (PostgreSQL) |


---

## ⚙️ 3. Services

### 3.1 staff-service

**Database:** MySQL  

**Chức năng:**
- Đăng nhập staff
- Nhập hàng
- Cập nhật sản phẩm

**API:**
- POST /staff/login
- POST /staff/products
- PUT /staff/products/{id}

---

### 3.2 customer-service

**Database:** MySQL  

**Chức năng:**
- Đăng ký
- Đăng nhập
- Tạo giỏ hàng

**API:**
- POST /customer/register
- POST /customer/login
- POST /customer/create-cart

---

### 3.3 cart-service

**Database:** PostgreSQL  

**Chức năng:**
- Thêm sản phẩm vào giỏ
- Xem giỏ hàng

**API:**
- POST /cart/add
- GET /cart/{customer_id}

---

### 3.4 laptop-service

**Database:** PostgreSQL  

**Chức năng:**
- CRUD laptop

**API:**
- GET /laptops
- POST /laptops
- PUT /laptops/{id}
- DELETE /laptops/{id}

---

### 3.5 clothes-service

**Database:** PostgreSQL  

**Chức năng:**
- CRUD clothes

**API:**
- GET /clothes
- POST /clothes
- PUT /clothes/{id}
- DELETE /clothes/{id}

---

## 🌐 4. API Gateway

### 4.1 Routing

- /staff/* → staff-service
- /customer/* → customer-service
- /cart/* → cart-service
- /laptops/* → laptop-service
- /clothes/* → clothes-service

---

### 4.2 UI

#### Staff UI
- Login
- Form nhập sản phẩm
- Form cập nhật sản phẩm

#### Customer UI
- Register / Login
- Xem sản phẩm
- Thêm vào giỏ hàng
- Xem giỏ hàng

---

## 🗄️ 5. Database

| Service           | Database     |
|------------------|-------------|
| staff-service    | MySQL       |
| customer-service | MySQL       |
| cart-service     | PostgreSQL  |
| laptop-service   | PostgreSQL  |
| clothes-service  | PostgreSQL  |

---

## 🔐 6. Authentication

- Sử dụng JWT
- Staff và Customer tách riêng

---

## 🔗 7. Communication

- Giao tiếp giữa các service qua REST API (HTTP)

---

## 🐳 8. Docker

### Mỗi service phải có:
- Dockerfile
- requirements.txt
- Expose port riêng

---

## 📦 9. Docker Compose

File: `docker-compose.yml` tại root `kiemtra01`

Bao gồm:
- 5 services
- 1 API Gateway
- 2 MySQL containers
- 3 PostgreSQL containers

---

## 📁 10. Project Structure
kiemtra01/
│
├── api-gateway/
├── staff-service/
├── customer-service/
├── cart-service/
├── laptop-service/
├── clothes-service/
│
├── docker-compose.yml


---

## 🚀 11. Run System
docker-compose up --build


---

## ✅ 12. Minimum Requirements (Để pass bài)

- API hoạt động
- Gateway routing đúng
- Database kết nối thành công
- Docker chạy được toàn bộ hệ thống

---

## ⚠️ 13. Notes

- Không cần production-level
- Có thể mock data
- Focus vào:
  - Kiến trúc microservice
  - Routing
  - Docker