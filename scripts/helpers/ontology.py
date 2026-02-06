BASE_RELATIONS = [
    "acquires",
    "invests_in",
    "is_fined",
    "sues",
    "partners_with",
    "controls",
    "has_exposure",
    "is_competitor_of",
    "is_member_of",
    "supplies",
    "has_positive_impact",
    "has_negative_impact",
]

ENTITY_TYPES = [
    "person",
    "company",
    "financial_institution",  # Banks, insurers, funds (subset of companies but explicit)
    "financial_instrument",   # Bonds, derivatives, stocks, loans (distinct tradable assets)
    "country",
    "city_region",
    "regulator",
    "disaster_event",         # Wars, hurricanes, political conflicts, pandemics
    "product_service",        # iPhone, AWS, Boeing 737
    "economic_indicator"     # GDP, CPI, unemployment, interest rates
]

ALLOWED_SECTORS = {
    "financials",
    "technology",
    "healthcare",
    "real_estate",
    "industrials",
    "transportation",
    "energy",
    "consumer_goods_and_services",
    "natural_resources",
    "public_sector"
}
ENTITY_TYPE_SYNONYMS = {

    # ───────────── person ─────────────
    "individual": "person",
    "human": "person",
    "executive": "person",
    "ceo": "person",
    "cfo": "person",
    "cto": "person",
    "founder": "person",
    "cofounder": "person",
    "chairman": "person",
    "chairwoman": "person",
    "director": "person",
    "manager": "person",
    "employee": "person",
    "politician": "person",
    "president": "person",
    "prime_minister": "person",

    # ───────────── company ─────────────
    "corporation": "company",
    "corp": "company",
    "firm": "company",
    "enterprise": "company",
    "business": "company",
    "organization": "company",
    "organisation": "company",
    "startup": "company",
    "scaleup": "company",
    "multinational": "company",
    "conglomerate": "company",
    "subsidiary": "company",
    "vendor": "company",
    "supplier": "company",
    "manufacturer": "company",

    # ───── financial institution ─────
    "bank": "financial_institution",
    "investment bank": "financial_institution",
    "commercial bank": "financial_institution",
    "central bank": "financial_institution",
    "insurer": "financial_institution",
    "insurance_company": "financial_institution",
    "hedge fund": "financial_institution",
    "private equity": "financial_institution",
    "venture capital": "financial_institution",
    "asset manager": "financial_institution",
    "pension fund": "financial_institution",
    "credit union": "financial_institution",
    "lender": "financial_institution",

    # ───── financial instrument ─────
    "stock": "financial_instrument",
    "share": "financial_instrument",
    "equity": "financial_instrument",
    "bond": "financial_instrument",
    "debt": "financial_instrument",
    "loan": "financial_instrument",
    "derivative": "financial_instrument",
    "option": "financial_instrument",
    "future": "financial_instrument",
    "swap": "financial_instrument",
    "security": "financial_instrument",
    "etf": "financial_instrument",
    "mutual_fund": "financial_instrument",
    "index_fund": "financial_instrument",
    "crypto_asset": "financial_instrument",
    "cryptocurrency": "financial_instrument",
    "token": "financial_instrument",

    # ───────────── country ─────────────
    "nation": "country",
    "state": "country",
    "republic": "country",

    # ───────── city / region ─────────
    "city": "city_region",
    "region": "city_region",
    "province": "city_region",
    "municipality": "city_region",
    "metropolitan area": "city_region",
    "territory": "city_region",

    # ───────────── regulator ─────────────
    "agency": "regulator",
    "authority": "regulator",
    "government agency": "regulator",
    "supervisory body": "regulator",
    "watchdog": "regulator",
    "commission": "regulator",
    "ministry": "regulator",
    "department": "regulator",

    # ────────── disaster / event ──────────
    "war": "disaster_event",
    "conflict": "disaster_event",
    "pandemic": "disaster_event",
    "epidemic": "disaster_event",
    "earthquake": "disaster_event",
    "hurricane": "disaster_event",
    "flood": "disaster_event",
    "wildfire": "disaster_event",
    "natural disaster": "disaster_event",
    "crisis": "disaster_event",

    # ─────── product / service ───────
    "product": "product_service",
    "service": "product_service",
    "platform": "product_service",
    "software": "product_service",
    "hardware": "product_service",
    "application": "product_service",
    "app": "product_service",
    "device": "product_service",
    "model": "product_service",

    # ───── economic indicator ─────
    "gdp": "economic_indicator",
    "inflation": "economic_indicator",
    "cpi": "economic_indicator",
    "ppi": "economic_indicator",
    "interest_rate": "economic_indicator",
    "unemployment_rate": "economic_indicator",
    "economic_growth": "economic_indicator",
    "trade_balance": "economic_indicator",
    "budget_deficit": "economic_indicator"
}

SECTOR_SYNONYMS = {
    # financials
    "finance": "financials",
    "financial": "financials",
    "banking": "financials",
    "investment": "financials",
    "insurance": "financials",
    "fintech": "financials",
    "wealth management" : "financials",
    
    # technology
    "tech": "technology",
    "information technology": "technology",
    "software": "technology",
    "hardware": "technology",
    "ai": "technology",
    "it": "technology",
    "app": "technology", 
    "web":"technology", 
    "media":"technology",

    # healthcare
    "health": "healthcare",
    "biotech": "healthcare",
    "pharma": "healthcare",
    "medical": "healthcare",

    # real estate
    "property": "real_estate",
    "housing": "real_estate",

    # industrials
    "industrial": "industrials",
    "manufacturing": "industrials",
    "construction": "industrials",
    "chemicals": "industrials",

    # transportation
    "transport": "transportation",
    "logistics": "transportation",
    "shipping": "transportation",
    "airlines": "transportation",

    # energy
    "oil": "energy",
    "gas": "energy",
    "energy sector": "energy",
    "utilities": "energy",
    "renewables": "energy",

    # consumer goods and services
    "consumer": "consumer_goods_and_services",
    "retail": "consumer_goods_and_services",
    "food": "consumer_goods_and_services",
    "beverages": "consumer_goods_and_services",
    "food and beverages": "consumer_goods_and_services",
    "apparel": "consumer_goods_and_services",
    "entertainment":"consumer_goods_and_services",
    "e-commerce": "consumer_goods_and_services",

    # natural resources
    "mining": "natural_resources",
    "metals": "natural_resources",
    "agriculture": "natural_resources",
    "timber": "natural_resources",
    "sustainability": "natural_resources",

    # public sector
    "government": "public_sector",
    "public": "public_sector",
    "state": "public_sector",
    "education": "public_sector",
    "social services":  "public_sector"
}

