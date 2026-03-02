"""
ams_scraper.py — MITS AMS Playwright Scraper
=============================================
WINDOWS FIX: Uses WindowsProactorEventLoopPolicy to prevent NotImplementedError.

INSTALL ONCE (run in CMD):
    pip install playwright beautifulsoup4
    python -m playwright install chromium
"""

import asyncio
import threading
import time
import re
import sys
import traceback

try:
    from playwright.async_api import async_playwright
    PW_OK = True
except ImportError:
    PW_OK = False

try:
    from bs4 import BeautifulSoup
    BS4_OK = True
except ImportError:
    BS4_OK = False

# Shared state
_state = {"status": "idle", "data": None, "error": ""}
_lock  = threading.Lock()


def get_state():
    with _lock:
        return dict(_state)


def reset_state():
    global _state
    with _lock:
        _state = {"status": "idle", "data": None, "error": ""}


def start_login(email: str) -> bool:
    with _lock:
        if _state["status"] == "running":
            return False
        _state["status"] = "running"
        _state["data"]   = None
        _state["error"]  = ""
    t = threading.Thread(target=_thread_entry, args=(email,), daemon=True)
    t.start()
    return True


def _thread_entry(email: str):
    # WINDOWS FIX: SelectorEventLoop cannot launch subprocesses on Windows.
    # WindowsProactorEventLoopPolicy supports subprocess (needed for Chrome).
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(_async_scrape(email))
    except Exception as e:
        err_msg = f"{type(e).__name__}: {e}"
        with _lock:
            _state["status"] = "error"
            _state["error"]  = err_msg
        print(f"[AMS FATAL] {err_msg}")
        traceback.print_exc()
    finally:
        try:
            loop.close()
        except Exception:
            pass


async def _async_scrape(email: str):
    global _state

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=30)
        ctx = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await ctx.new_page()

        print("[AMS] Opening AMS login...")
        try:
            await page.goto(
                "https://ams.mitsgwalior.in/login",
                wait_until="domcontentloaded",
                timeout=30000
            )
        except Exception as e:
            await browser.close()
            with _lock:
                _state["status"] = "error"
                _state["error"]  = f"Cannot reach AMS. Check internet. ({type(e).__name__})"
            return

        print(f"[AMS] Waiting for Google sign-in ({email})...")

        deadline  = time.time() + 180
        logged_in = False

        while time.time() < deadline:
            try:
                url = page.url
                if (
                    "mitsgwalior.in" in url
                    and "/login" not in url
                    and "accounts.google.com" not in url
                    and "google.com/o/oauth" not in url
                ):
                    logged_in = True
                    print(f"[AMS] Login OK: {url}")
                    break
            except Exception:
                pass
            await asyncio.sleep(1)

        if not logged_in:
            await browser.close()
            with _lock:
                _state["status"] = "error"
                _state["error"]  = "Timeout — you did not sign in within 3 minutes."
            return

        await asyncio.sleep(3)
        print("[AMS] Reading dashboard...")

        try:
            await page.goto(
                "https://ams.mitsgwalior.in/student/dashboard",
                wait_until="networkidle",
                timeout=15000
            )
            await asyncio.sleep(2)
        except Exception:
            pass

        dash_html = await page.content()

        result = {
            "name": "",
            "enrollment": email.split("@")[0],
            "total_courses": 0,
            "total_classes": 0,
            "classes_attended": 0,
            "overall_pct": 0.0,
            "overall_status": "",
            "subjects": []
        }

        m = re.search(r"Welcome back[,\s]+([A-Z][A-Z\s]+?)!", dash_html)
        if m:
            result["name"] = m.group(1).strip().title()

        for key, pattern in [
            ("total_courses",    r"Total Courses[^\d]*(\d+)"),
            ("total_classes",    r"Total Classes[^\d]*(\d+)"),
            ("classes_attended", r"Classes Attended[^\d]*(\d+)"),
        ]:
            mm = re.search(pattern, dash_html, re.I)
            if mm:
                result[key] = int(mm.group(1))

        mm = re.search(r"Overall Percentage[^\d]*([\d.]+)", dash_html, re.I)
        if mm:
            result["overall_pct"] = float(mm.group(1))

        mm = re.search(r"\b(At Risk|Good|Safe|Excellent)\b", dash_html, re.I)
        if mm:
            result["overall_status"] = mm.group(1)

        print("[AMS] Reading courses...")
        try:
            await page.goto(
                "https://ams.mitsgwalior.in/student/courses",
                wait_until="networkidle",
                timeout=15000
            )
            await asyncio.sleep(2)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1.5)
        except Exception:
            pass

        courses_html = await page.content()
        subjects = _parse_subjects(courses_html)

        if not subjects:
            subjects = _parse_subjects(dash_html)

        result["subjects"] = subjects

        if result["overall_pct"] == 0.0 and subjects:
            result["overall_pct"] = round(
                sum(s["pct"] for s in subjects) / len(subjects), 1
            )

        if not result["name"]:
            result["name"] = email.split("@")[0].replace(".", " ").title()

        await browser.close()
        print(f"[AMS] Done: {len(subjects)} subjects, {result['overall_pct']}%")

        with _lock:
            _state["status"] = "done"
            _state["data"]   = result


def _parse_subjects(html: str) -> list:
    subjects = []

    if not BS4_OK:
        blocks = list(re.finditer(
            r'Attendance:\s*([\d.]+)%.*?Classes:\s*(\d+)\s*/\s*(\d+)',
            html, re.DOTALL | re.I
        ))
        for i, b in enumerate(blocks):
            subjects.append({
                "name": f"Subject {i+1}", "code": "", "type": "",
                "pct": float(b.group(1)),
                "attended": int(b.group(2)),
                "held": int(b.group(3)),
                "faculty": "", "semester": ""
            })
        return subjects

    soup = BeautifulSoup(html, "html.parser")

    for el in soup.find_all(["div", "article", "li", "section"]):
        text = el.get_text(" ", strip=True)

        if "Attendance:" not in text or "Classes:" not in text:
            continue
        if text.count("Attendance:") > 2:
            continue

        subj = {
            "name": "", "code": "", "type": "",
            "pct": 0.0, "attended": 0, "held": 0,
            "faculty": "", "semester": ""
        }

        for tag in ["h2", "h3", "h4", "h5", "strong", "b"]:
            heading = el.find(tag)
            if heading:
                t = heading.get_text(strip=True)
                if t and len(t) > 1 and re.search(r'[A-Za-z]', t) and len(t) < 100:
                    subj["name"] = t
                    break

        if not subj["name"]:
            continue

        for small in el.find_all(["p", "span", "small", "div"]):
            t = small.get_text(strip=True)
            if re.fullmatch(r'[A-Z0-9]{5,20}', t) and t != subj["name"]:
                subj["code"] = t
                break
        if not subj["code"]:
            cm = re.search(r'\b(\d{5,10}|[A-Z]{2,6}\d{3,8})\b', text)
            if cm and cm.group(1) not in subj["name"]:
                subj["code"] = cm.group(1)

        am = re.search(r'Attendance:\s*([\d.]+)\s*%', text, re.I)
        if am:
            subj["pct"] = float(am.group(1))

        cm2 = re.search(r'Classes:\s*(\d+)\s*/\s*(\d+)', text, re.I)
        if cm2:
            subj["attended"] = int(cm2.group(1))
            subj["held"]     = int(cm2.group(2))

        for t_type in ["THEORY", "LAB", "NEC", "PRACTICAL", "ELECTIVE"]:
            if t_type in text.upper():
                subj["type"] = t_type
                break

        fm = re.search(r'Faculty:\s*([A-Za-z][A-Za-z\s\.]{2,40}?)(?:\s{2,}|Sem|\d|$)', text)
        if fm:
            subj["faculty"] = fm.group(1).strip()

        sm = re.search(r'Sem\s*(\d)', text, re.I)
        if sm:
            subj["semester"] = f"Sem {sm.group(1)}"

        if subj["pct"] > 0:
            is_dup = any(
                s["name"] == subj["name"] and s["code"] == subj["code"]
                for s in subjects
            )
            if not is_dup:
                subjects.append(subj)

    return subjects
