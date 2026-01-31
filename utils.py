import time, random, string, re, json

def generate_device_id():
    prefix = "75"
    ts = str(int(time.time()))[-10:]
    rnd = "".join(random.choices(string.digits, k=7))
    return prefix + ts + rnd

def extract_tokens(headers, cookies, html):
    # 1. Try Cookie Jar
    ms_token = cookies.get("msToken")
    
    # 2. Try raw headers
    if not ms_token:
        h_c = headers.get("set-cookie", "") or headers.get("Set-Cookie", "")
        match = re.search(r'msToken=([^; ]+)', h_c)
        ms_token = match.group(1) if match else None
        
    # 3. Try HTML Body (SIGI_STATE)
    if not ms_token:
        match = re.search(r'msToken\\":\\"(.*?)\\"', html)
        if not match: match = re.search(r'"msToken":"(.*?)"', html)
        ms_token = match.group(1) if match else None
    
    odin_id = re.search(r'"odinId":"(.*?)"', html)
    if not odin_id: odin_id = re.search(r'odinId\\":\\"(.*?)\\"', html)
    
    return ms_token, odin_id.group(1) if odin_id else None
