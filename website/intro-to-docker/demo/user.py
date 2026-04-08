import requests
import json

url = "https://infser-90695129128.us-west2.run.app/predict"

payload = {"feature1" : 1, "feature2" : 2, "feature3" : 3, "feature4" : 4}

headers = {"Content-Type": "application/json"}
response = requests.post(url, data=json.dumps(payload), headers=headers)
print("Status:", response.status_code)

print(response.text)

# Or you can use Postman.
# https://www.postman.com/