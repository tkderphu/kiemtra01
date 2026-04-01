📦 4. ORDER SERVICE (CORE)
🎯 Responsibility
Tạo đơn hàng
Orchestrate các service khác
Quản lý trạng thái tổng thể
🗃️ Schema (PostgreSQL)
Order
Order:
- id (UUID)
- user_id
- status
- total_amount
- currency
- payment_status
- shipping_status
- created_at
- updated_at
OrderItem
OrderItem:
- id
- order_id
- product_id
- product_type   -- laptop | clothes
- quantity
- price_snapshot
🔗 APIs
1. Create Order
POST /orders/
Request
{
  "user_id": 1,
  "items": [
    {
      "product_id": "uuid",
      "type": "laptop",
      "quantity": 1
    },
    {
      "product_id": "uuid",
      "type": "clothes",
      "quantity": 2
    }
  ]
}
🔥 FLOW CHI TIẾT
Group items theo type
Call:
Laptop Service → check + reserve
Clothes Service → check + reserve
Nếu OK → tạo order
Gọi Payment Service
Trả về payment_url
2. Payment Callback
POST /orders/payment-callback/
Logic
SUCCESS:
update payment_status
confirm stock (product services)
gọi Shipping Service
FAILED:
release stock
cancel order
3. Shipping Callback
POST /orders/shipping-callback/
4. Get Order
GET /orders/{id}/
💳 5. PAYMENT SERVICE
🎯 Responsibility
Tạo payment
Handle payment gateway callback
🗃️ Schema
Payment:
- id
- order_id
- amount
- status
- transaction_id
🔗 APIs
1. Create Payment
POST /payments/
2. Callback từ Gateway
POST /payments/callback/
🔥 FLOW
Gateway → Payment Service
        → Order Service
🚚 6. SHIPPING SERVICE
🎯 Responsibility
Tạo shipment
Tracking
🗃️ Schema
Shipment:
- id
- order_id
- address
- status
- tracking_number
🔗 APIs
1. Create Shipment
POST /shipments/
2. Update Status
PATCH /shipments/{id}/status/
3. Callback
POST /orders/shipping-callback/
🔄 7. LUỒNG NGHIỆP VỤ (SAGA)
🛒 ORDER FLOW
Create Order
   ↓
Reserve Stock (Laptop + Clothes)
   ↓
Create Payment
💰 PAYMENT SUCCESS
Payment Success
   ↓
Confirm Stock
   ↓
Create Shipment
❌ PAYMENT FAIL
Payment Failed
   ↓
Release Stock
   ↓
Cancel Order
🚚 SHIPPING
Shipping Delivered
   ↓
Order Completed
🔗 8. SERVICE COMMUNICATION
Sync APIs
From	To	API
Order	Laptop	/reserve
Order	Clothes	/reserve
Order	Payment	/payments
Payment	Order	/payment-callback
Order	Shipping	/shipments
Shipping	Order	/shipping-callback