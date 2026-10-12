import subprocess, json, sys, os, time

server_path = r'c:\Users\Admin\Downloads\Sales-support-AI-pilot\mcp_server_pytutor.py'
proc = subprocess.Popen(
    [sys.executable, '-u', server_path],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
)
time.sleep(0.5)

def send(msg):
    body = json.dumps(msg).encode('utf-8')
    proc.stdin.write(f'Content-Length: {len(body)}\r\n\r\n'.encode('utf-8') + body)
    proc.stdin.flush()

def recv():
    headers = {}
    while True:
        line = proc.stdout.readline().decode('utf-8')
        if not line or line == '\r\n': break
        if ':' in line:
            k,v = line.strip().split(':',1)
            headers[k.strip()] = v.strip()
    n = int(headers.get('Content-Length', 0))
    return json.loads(proc.stdout.read(n)) if n else {}

# Handshake
send({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}}})
r = recv()
print('Init OK:', r.get('result',{}).get('serverInfo',{}))
send({'jsonrpc':'2.0','method':'notifications/initialized'})

# List tools
send({'jsonrpc':'2.0','id':2,'method':'tools/list'})
r = recv()
print('Tools:', [t['name'] for t in r.get('result',{}).get('tools',[])])

# Call run_code
code = 'n=5\ntong=sum(range(1,n+1))\nprint(f"Sum 1..{n} = {tong}")'
send({'jsonrpc':'2.0','id':3,'method':'tools/call','params':{'name':'run_code','arguments':{'code':code}}})
r = recv()
print('Result:', r.get('result',{}).get('content',[{}])[0].get('text',''))

proc.terminate()
