import re

norm = "Securities Limited ICICI Venture House, Appasaheb Marathe Marg, Prabhadevi, Mumbai 400025, Maharashtra, India Tel: +91 2"
idx_house = norm.find("House")
pre_win = norm[max(0, idx_house-45):idx_house]
print("pre_win before House:", repr(pre_win))

pre_m = re.search(r"((?:[A-Z][A-Za-z0-9&.'()-]*\s+){1,3})$", pre_win)
if pre_m:
    words = pre_m.group(1).strip().split()
    clean_words = [w for w in words if w.lower() not in ("limited", "llp", "ltd", "inc", "pvt", "private")]
    if clean_words:
        clean_prefix = " ".join(clean_words) + " "
        print("clean_prefix:", repr(clean_prefix))
        start_idx = idx_house - len(clean_prefix)
        print("Full address:", repr(norm[start_idx:norm.find("India")+5]))
