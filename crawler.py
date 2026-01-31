import asyncio, json, time, random
from urllib.parse import urlencode, quote
from curl_cffi.requests import AsyncSession
from email.utils import parsedate_to_datetime
import config, algorithms, utils

class TikTokCrawler:
    def __init__(self):
        proxies = {"http": config.PROXY_URL, "https": config.PROXY_URL} if config.PROXY_URL else None
        self.session = AsyncSession(
            impersonate=config.IMPERSONATE_LABEL, 
            proxies=proxies,
            headers={"User-Agent": config.USER_AGENT, "Accept": "*/*", "Connection": "keep-alive"}
        )
        self.device_id = utils.generate_device_id()
        self.ms_token = None
        self.server_offset = 0

    async def init_session(self):
        print(f"[*] Handshake: Warming via {'Proxy' if config.PROXY_URL else 'Local IP'}...")
        # Step 1: Hit Video Page directly (Best for token issuance)
        target_url = f"https://www.tiktok.com/@user/video/{config.TARGET_VIDEO_ID}"
        resp = await self.session.get(target_url, timeout=20)
        
        # Step 2: Extract tokens using deep logic
        self.ms_token, _ = utils.extract_tokens(
            resp.headers, self.session.cookies.get_dict(), resp.text
        )
        
        # Step 3: Time Sync
        s_date = resp.headers.get("date") or resp.headers.get("Date")
        if s_date:
            self.server_offset = int(parsedate_to_datetime(s_date).timestamp()) - int(time.time())

        if self.ms_token:
            print(f"[+] Handshake Success. msToken: {self.ms_token[:10]}...")
            return True
        return False

    async def fetch_comments(self, video_id: str):
        if not self.ms_token:
            await self.init_session()

        ts = int(time.time() + self.server_offset)
        params = [
            ("aid", "1988"), ("aweme_id", video_id), ("count", "20"), ("cursor", "0"),
            ("device_id", self.device_id), ("msToken", self.ms_token or ""),
        ]
        
        query = urlencode(params, quote_via=quote)
        sigs = algorithms.get_signatures(query, config.USER_AGENT, ts)
        full_url = f"{config.BASE_URL}?{query}&X-Bogus={sigs['X-Bogus']}"
        
        headers = {"X-Gnarly": sigs['X-Gnarly'], "Referer": "https://www.tiktok.com/"}

        print(f"[*] Request Sent. msToken: {'FOUND' if self.ms_token else 'MISSING'}")
        
        resp = await self.session.get(full_url, headers=headers, timeout=30)
        
        if resp.text.strip().startswith('{'):
            return resp.json()
        return {"error": "WAF_BLOCK", "reason": "Server returned HTML/Captcha", "token_status": "MISSING" if not self.ms_token else "PRESENT"}

async def main():
    bot = TikTokCrawler()
    # Try local run if proxy is failing in config
    await bot.init_session()
    data = await bot.fetch_comments(config.TARGET_VIDEO_ID)
    print("\n--- API RESPONSE ---")
    print(json.dumps(data, indent=4))
    await bot.session.close()

if __name__ == "__main__": asyncio.run(main())
