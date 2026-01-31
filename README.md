# TikTok-V5-API-Scraper--DD
High-performance asynchronous TikTok Scraper. Pure Python implementation of X-Bogus v5 and X-Gnarly signatures. Features TLS fingerprinting bypass (JA3/JA4) using curl_cffi and automated session handshake logic.



# TikTok API Scraper (v5) - Pure Python Implementation

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Working-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

A sophisticated, asynchronous reverse-engineered solution for the TikTok Web API (2026 Standards). 

This project demonstrates how to generate the complex cryptographic signatures (**X-Bogus** and **X-Gnarly**) required to communicate with TikTok's backend, while bypassing WAF protections and TLS Fingerprinting checks.

**⚠️ Disclaimer: This repository is for EDUCATIONAL and RESEARCH purposes only.**

## 🚀 Key Features

*   **Pure Python Cryptography:** No Node.js runtime or external APIs required. 
    *   Full implementation of `X-Bogus` (v5.1) algorithm (RC4 encryption, Bitwise shuffling).
    *   Full implementation of `X-Gnarly` (0404) header generation.
*   **TLS Fingerprint Bypass:** Uses `curl_cffi` to impersonate real browser TLS handshakes (Chrome 124), bypassing Akamai/Cloudflare bot detection.
*   **Automated Session Handshake:** Implements a "Cold Start" logic to visit the video page, solve the initial challenge, and acquire valid `ttwid`, `msToken`, and `odinId` cookies.
*   **Fallback Token Injection:** Includes logic to generate mathematically valid fallback tokens if the proxy handshake is interrupted.
*   **Asynchronous Architecture:** Built on `asyncio` for high-concurrency scraping.

## 🛠️ Technology Stack

*   **Language:** Python 3.x
*   **Network:** `curl_cffi` (for TLS Impersonation)
*   **Crypto:** `hashlib`, `base64` (Standard Libs)

## ⚙️ Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/YOUR_USERNAME/tiktok-v5-scraper.git
    cd tiktok-v5-scraper
    ```

2.  Install dependencies:
    ```bash
    pip install curl-cffi
    ```

3.  **Configuration:**
    Open `config.py` and add your Proxy.
    *   *Note: High-quality Residential Proxies are recommended to avoid Captchas during the handshake.*

## 🧠 Technical Deep Dive

### The Challenge
TikTok's API is protected by multiple layers of security:
1.  **Request Signing:** Modifying any URL parameter without updating the `X-Bogus` signature results in a block.
2.  **Browser Consistency:** The `X-Gnarly` header binds the request to specific browser attributes and timestamps.
3.  **TLS Fingerprinting:** Standard Python requests (`urllib`, `requests`) are blocked at the TCP/IP level.

### The Solution
This scraper emulates a full browser environment:
1.  **Token Acquisition:** It performs a "Warmup" request to the target video page to synchronize cookies (`tt_chain_token`, `ttwid`) with the specific video context.
2.  **Signature Generation:** It takes the query parameters, User-Agent, and Timestamp, and processes them through a custom RC4/MD5 algorithm derived from the obfuscated `signer.js` SDK.
3.  **Header Ordering:** It enforces strict HTTP header ordering to match Chrome's network stack behavior.

## 📋 Usage

```python
# main.py runs the full workflow
python crawler.py
