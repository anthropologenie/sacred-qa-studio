import re, httpx

# very simple GA4 / GTM presence heuristics
GA4_RE   = re.compile(r"gtag\\(\\'config\\',\\s*['\"]G-[A-Z0-9]+['\"]\\)")
GTM_RE   = re.compile(r"googletagmanager.com/gtm.js\\?id=GTM-")
META_RE  = re.compile(r"connect\\.facebook\\.net/.*/fbevents\\.js")

async def check_pixels(url: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, follow_redirects=True)
    html = r.text
    found = {
        "ga4": bool(GA4_RE.search(html)),
        "gtm": bool(GTM_RE.search(html)),
        "meta": bool(META_RE.search(html)),
    }
    status = "pass" if any(found.values()) else "warning"
    return {"check":"pixel_presence","status":status,"details":found}
