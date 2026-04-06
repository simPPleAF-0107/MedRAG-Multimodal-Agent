import urllib.request, urllib.parse, json

# Step 1: Login to get token
login_data = urllib.parse.urlencode({'username': 'dr.smith@medrag.com', 'password': 'password123'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/api/v1/auth/login', data=login_data)
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
with urllib.request.urlopen(req, timeout=10) as resp:
    token = json.loads(resp.read()).get('access_token', '')
print('Auth token acquired:', bool(token))

# Step 2: Call generate-report (multipart/form-data)
boundary = '----MedRAGBoundary'
lines = [
    '--' + boundary,
    'Content-Disposition: form-data; name="query"',
    '',
    'Patient has severe stomach ache and nausea after alcohol last night. History of gastritis.',
    '--' + boundary + '--',
    ''
]
body = '\r\n'.join(lines).encode()

req2 = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/rag/generate-report',
    data=body, method='POST'
)
req2.add_header('Authorization', 'Bearer ' + token)
req2.add_header('Content-Type', 'multipart/form-data; boundary=' + boundary)

print('Calling /rag/generate-report (may take up to 5 min for full LangGraph pipeline)...')
try:
    with urllib.request.urlopen(req2, timeout=300) as resp:
        result = json.loads(resp.read())
        print()
        print('=== DIAGNOSTIC INFERENCE ENGINE RESULT ===')
        print('diagnosis[:350]   :', result.get('diagnosis', '')[:350])
        print('risk_score        :', result.get('risk_score'))
        print('risk_level        :', result.get('risk_assessment', {}).get('risk_level'))
        print('emergency_flag    :', result.get('emergency_flag'))
        print('confidence_score  :', result.get('confidence_score'))
        print('recommended_spec  :', result.get('recommended_specialty'))
        diffs = result.get('differential_diagnosis', [])
        print('differential[:2]  :', diffs[:2])
        print('final_report[:200]:', str(result.get('final_report', ''))[:200])
        print('status            :', result.get('status'))
except urllib.error.HTTPError as e:
    print('HTTP Error:', e.code, e.read().decode()[:500])
except Exception as e:
    print('Error:', type(e).__name__, e)
