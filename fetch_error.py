import requests

try:
    res = requests.get('http://localhost:8000/laptops')
    with open('debug_laptop.html', 'w', encoding='utf-8') as f:
        f.write(res.text)
        
    res2 = requests.get('http://localhost:8000/clothes')
    with open('debug_clothes.html', 'w', encoding='utf-8') as f:
        f.write(res2.text)
except Exception as e:
    with open('debug_err.txt', 'w', encoding='utf-8') as f:
        f.write(str(e))
