import unittest
import requests
import time
import random

BASE_URL = "http://localhost:8000"

class SystemE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Starting System End-to-End Tests...")
        # Check if API Gateway is reachable
        try:
            requests.get(f"{BASE_URL}/laptops", timeout=3)
        except requests.exceptions.ConnectionError:
            print("ERROR: API Gateway is not running at http://localhost:8000")
            print("Please run `docker-compose up --build -d` first.")
            exit(1)

    def setUp(self):
        # Generate a unique username for each test run to avoid conflict
        self.username = f"e2e_user_{random.randint(10000, 99999)}"
        self.password = "secure_pass"
        self.customer_id = None
        self.token = None
        
        # Test Data Target
        self.test_laptop_id = 1  # Assuming at least 1 laptop exists in DB
        self.order_id = None
        self.payment_url = None

    def test_full_business_flow(self):
        """
        Flow:
        1. Register & Login
        2. Get products & Add to cart
        3. Checkout (Triggers SAGA: Order -> Reserve Stock -> Init Payment)
        4. Mock Payment Success (Triggers SAGA: Shipping)
        5. Verify Shipping & Order Status
        6. Submit a Comment (Verifies Purchase check)
        """
        
        # --- 1. AUTHENTICATION ---
        print(f"\n[Step 1] Registering {self.username}...")
        res = requests.post(f"{BASE_URL}/customer/register", json={
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(res.status_code, 201, f"Failed to register. Response: {res.text}")
        
        print("[Step 1] Logging in...")
        res = requests.post(f"{BASE_URL}/customer/login", json={
            "username": self.username,
            "password": self.password
        })
        self.assertEqual(res.status_code, 200, "Failed to login")
        data = res.json()
        self.customer_id = data.get("customer_id")
        self.token = data.get("token")
        self.assertIsNotNone(self.customer_id)

        # --- 2. ADD TO CART ---
        print("[Step 2] Adding product to Cart...")
        res = requests.post(f"{BASE_URL}/cart/add", json={
            "customer_id": self.customer_id,
            "product_id": self.test_laptop_id,
            "qty": 2
        })
        self.assertEqual(res.status_code, 200, "Failed to add to cart")

        # --- 3. CHECKOUT SAGA MULTI-STEP ---
        print("[Step 3] Checking out (SAGA Orchestration starting)...")
        # Fetch cart
        cart_res = requests.get(f"{BASE_URL}/cart/{self.customer_id}")
        cart_items = cart_res.json().get('items', [])
        self.assertTrue(len(cart_items) > 0)
        
        # Build Order Payload
        checkout_payload = {
            "user_id": self.customer_id,
            "items": [
                {
                    "product_id": item['product_id'],
                    "type": "laptops",
                    "quantity": item['qty'],
                    "price": 1000000  # Mock price for test
                } for item in cart_items
            ]
        }
        
        res = requests.post(f"{BASE_URL}/orders", json=checkout_payload)
        self.assertEqual(res.status_code, 201, f"Failed to checkout! SAGA Reserve failed? Error: {res.text}")
        
        order_data = res.json()
        self.order_id = order_data["order"]["id"]
        self.payment_url = order_data.get("payment_url")
        self.assertIsNotNone(self.payment_url, "Payment URL was not generated!")
        print(f" -> Order created successfully! ID: {self.order_id}")

        # --- 4. PAYMENT CALLBACK ---
        print("[Step 4] Mocking Payment Webhook Callback (SUCCESS)...")
        payment_id = self.payment_url.split("pay_id=")[1]
        
        res = requests.post(f"{BASE_URL}/payments/callback", json={
            "payment_id": payment_id,
            "action": "SUCCESS"
        })
        self.assertEqual(res.status_code, 200, "Payment webhook failed")

        # Give SAGA Orchestrator a moment to asynchronously update everything
        print(" -> Waiting 2 seconds for SAGA Shipping Callback convergence...")
        time.sleep(2)

        # --- 5. VERIFY FINAL STATUS ---
        print("[Step 5] Verifying Order & SAGA Status in Database...")
        res = requests.get(f"{BASE_URL}/orders")
        all_orders = res.json()
        my_order = next((o for o in all_orders if o['id'] == self.order_id), None)
        
        self.assertIsNotNone(my_order)
        self.assertEqual(my_order['payment_status'], "SUCCESS")
        
        shipping_status = my_order.get('shipping_status')
        # At this point, shipping should be PENDING or SHIPPED depending on mapping, 
        # but the order itself might not be DELIVERED yet.
        self.assertIsNotNone(shipping_status)
        print(f" -> Order Status Verified! Current Shipping: {shipping_status}")

        # --- 6. ATTEMPT COMMENT (SHOULD FAIL) ---
        print("[Step 6] Attempting to comment before Delivery (Should FAIL)...")
        res = requests.post(f"{BASE_URL}/comments", json={
            "user_id": self.customer_id,
            "product_id": self.test_laptop_id,
            "product_type": "laptops",
            "content": "Sản phẩm tuyệt vời!",
            "rating": 5
        })
        self.assertEqual(res.status_code, 403, "Comment should NOT be allowed before delivery")
        
        # --- 7. COMPLETE DELIVERY & COMMENT ---
        print("[Step 7] Mocking Shipping Delivery...")
        # Get shipment ID
        res = requests.get(f"{BASE_URL}/shipments")
        shipments = res.json()
        my_shipment = next((s for s in shipments if s['order_id'] == self.order_id), None)
        self.assertIsNotNone(my_shipment)
        
        shipment_id = my_shipment['id']
        res = requests.patch(f"{BASE_URL}/shipments/{shipment_id}/status", json={
            "status": "DELIVERED"
        })
        self.assertEqual(res.status_code, 200, "Failed to update shipment status to DELIVERED")

        time.sleep(1) # wait for Order webhook convergence
        
        print(" -> Proceeding to rate product...")
        res = requests.post(f"{BASE_URL}/comments", json={
            "user_id": self.customer_id,
            "product_id": self.test_laptop_id,
            "product_type": "laptops",
            "content": "Mình vừa nhận hàng, đóng gói rất đẹp!",
            "rating": 5
        })
        self.assertEqual(res.status_code, 201, f"Failed to comment even after delivery! Error: {res.text}")
        print(" -> ✅ Comment submitted successfully!")
        
        # Verify comment publicly visible
        res = requests.get(f"{BASE_URL}/comments/laptops/{self.test_laptop_id}")
        self.assertEqual(res.status_code, 200)
        verify_data = res.json()
        self.assertTrue(verify_data['total_comments'] >= 1)
        self.assertEqual(verify_data['average_rating'], 5.0)

        print("\n🎉 ALL E2E SAGA & MICROSERVICES TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == '__main__':
    unittest.main()
