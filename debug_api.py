import urllib.request
import json

try:
    req = urllib.request.urlopen("http://localhost:8000/laptops")
    print("LAPTOPS:", req.read().decode())
except Exception as e:
    print("LAPTOPS ERROR:", e)

try:
    req = urllib.request.urlopen("http://localhost:8000/clothes")
    print("CLOTHES:", req.read().decode())
except Exception as e:
    print("CLOTHES ERROR:", e)

try:
    req = urllib.request.urlopen("http://localhost:8000/customer/login") # Will fail method not allowed but shows if service responds
    print("CUSTOMER:", req.read().decode())
except Exception as e:
    print("CUSTOMER ERROR:", e)
