import re
import fitz
import redact_pii

doc = fitz.open("test_p5_in.pdf")
p = doc[0]
raw = p.get_text("text")
norm = redact_pii.normalize(raw)

PIN_RE = re.compile(r"(?<!\d)\d{3}\s?\d{3}(?!\d)")
ADDR_START_RE = re.compile(
    r"(?i)\b(?:[A-Z]-\d{1,4}|\d{1,4}\s*-\s*\d{1,4}|\d{1,4}(?:/\d{1,4})+|\d{1,4},|PCNTDA|Gat No\.?|Plot No\.?|S\.?\s?no\.?|CTS No\.?|Flat No\.?|Wing\s+[A-Z]|Tower\s+\d+|Building\s+No\.?\s*\d+)\b"
)
ADDRESS_KEYWORDS = re.compile(
    r"(?i)\b(?:road|street|marg|lane|village|taluka|district|plot|tower|floor|block|"
    r"building|campus|park|complex|house|apartment|society|nagar|chambers|bunglow|"
    r"bungalow|industrial area|phase|sector|farm|facility|colony)\b"
)

for pin in PIN_RE.finditer(norm):
    if "400025" in norm[pin.start():pin.end()]:
        start = max(0, pin.start() - 250)
        window = norm[start:pin.end()]
        candidates = []
        for m in ADDR_START_RE.finditer(window):
            candidates.append(m.start())
        for m in ADDRESS_KEYWORDS.finditer(window):
            candidates.append(m.start())
        s = min(candidates)
        pre_win = window[max(0, s-45):s]
        print("s matched:", repr(window[s:s+20]))
        print("pre_win:", repr(pre_win))
        pre_m = re.search(r"((?:[A-Z][A-Za-z0-9&.'()-]*\s+){1,3})$", pre_win)
        if pre_m:
            words = pre_m.group(1).strip().split()
            clean = [w for w in words if w.lower() not in ("limited", "llp", "ltd", "inc", "pvt", "private")]
            if clean:
                clean_str = " ".join(clean) + " "
                s_new = s - len(clean_str)
                print("clean_str:", repr(clean_str))
                print("new address:", repr(window[s_new:]))
