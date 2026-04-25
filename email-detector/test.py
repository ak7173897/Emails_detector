import urllib.request
import json

data = {"text": "Congratulations, you have won a lot of money! Click here to claim your prize!"}
req = urllib.request.Request("http://localhost:5000/predict", data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Status Code:", response.status)
        print("Response JSON:", json.loads(response.read().decode('utf-8')))
except Exception as e:
    print("Error:", e)
