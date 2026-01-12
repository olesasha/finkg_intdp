import pandas as pd 

def parse_text(path:str):
    """ Parse ARTICLE blocks into clean dictionaries and write them into a dataframe"""
    rows = []

    with open(path, "r", encoding="latin-1") as f:
        text = f.read()
        
    articles = re.split(r"(?=== ARTICLE \d+ ===)", text)[1:]
    
    for art in articles: 
        date = re.search(r"DATE:\s*(.+)", art)
        date = date.group(1).strip() if date else None
        
        url = re.search(r"URL:\s*(.+?)(?=TRIPLETS_RAW|\n|$)", art, flags=re.S)
        url = url.group(1).strip() if url else None
        
        # including possible truncation
        tr = re.search(r"TRIPLETS_RAW:\s*(\[.*)", art, flags=re.S)
        raw_triplets = tr.group(1) if tr else ""
    
        # ensure it starts with '['
        if not raw_triplets.startswith("["):
            raw_triplets = "[" + raw_triplets
            
        # cut off incomplete tail at last ']'
        last_bracket = raw_triplets.rfind("]")
        raw_triplets = raw_triplets[: last_bracket + 1] + "]"
    
        rows.append({"DATE": date, "URL": url, "TRIPLETS": raw_triplets})

    return pd.DataFrame(rows)
