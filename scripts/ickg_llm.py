from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

MODEL_NAME = "victorlxh/ICKG-v3.2"  # KG-construction model [web:311]

BASE_RELATIONS = [
    "acquisition",
    "relates_to",
    "invests_in",
    "fine",
    "lawsuit",
    "partnership",
    "has_positive_impact",
    "has_negative_impact",
    "controls",
    "has_exposure",
    "is_competitor_of",
    "is_member_of",
    "other"
]

ENTITY_TYPES = [
    "person",
    "company",
    "country",
    "regulator",
    "event",
    "product",
    "financial_institution",
    "financial_instrument",
    "economic_indicator",
    "sector", 
    "other"
]

_device = "cuda" if torch.cuda.is_available() else "cpu"
_pipe = None

def get_pipeline():
    global _pipe
    if _pipe is None:
        print(f"Loading {MODEL_NAME} on {_device}...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

        if _device == "cuda":
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
                device_map="auto",
            )
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
            )  # no device= with device_map
        else:
            model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                dtype=torch.float16,
            )
            _pipe = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=-1,
            )
    return _pipe

def generate(prompt: str, max_new_tokens: int = 512) -> str:
    pipe = get_pipeline()
    out = pipe(
        prompt,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        temperature=0.0,
        pad_token_id=pipe.tokenizer.eos_token_id,
    )
    return out[0]["generated_text"]

if __name__ == "__main__":
    article_text = """
Russia’s invasion of Ukraine has profoundly altered how Europe conceives of war.
Gone are the days when a handful of defense conglomerates waited on ministers to greenlight billion-euro programs before daring to manufacture. Amid uncertainty about US military support, leaders in Germany and other states have recognized they need to bolster their defenses. The European Defense Agency estimates that the EU will invest approximately €130 billion (about $151 billion) in defense this year, up from €106 billion in 2024. At the same time, venture capitalists have invested $1.5 billion in European defense startups, according to Oxford Analytica.
Of the more than 230 startups founded since 2022, German companies such as Helsing, EuroAtlas, Quantum Systems or ARX Robotics offer real change to their government’s defense ministry, eager to triple its budget. Helsing, for instance, is an outfit that provides Ukraine with drones, which are then updated every few weeks. ARX Robotics is developing spy cockroaches, equipped with cameras, that can collect information in hostile territory. EuroAtlas builds autonomous underwater vehicles that can monitor cables on the ocean floor. Finally, Quantum Systems is developing a drone that intercepts and neutralizes hostile unmanned aircraft.
German companies are at the forefront of the battle, but they are not alone. Tekever, a Portuguese entity with offices in the UK, the US, and France, manufactures a variety of drones that are quickly tested in Ukraine. British startups are also redesigning the battlefield. Kraken Technologies has two plants in the UK and, soon, a third in Hamburg, Germany. Its star product, K3 Scout, is an autonomous unmanned surface vehicle that can carry various weapon platforms onto the high seas.
Cambridge Aerospace, another UK startup, was co-founded by Steven Barrett, an aerospace engineer and Cambridge University professor. The company, created in 2024, focuses on making inexpensive drones to intercept ballistic missiles.
France, the startup nation dreamed by President Emmanuel Macron, refuses to be outpaced. Harmattan AI, founded in 2024, has already secured contracts with the French and British defense ministries. It is producing 1,000 autonomous reconnaissance and combat drones for the French military, while Alta Ares refines battlefield intelligence software that processes drone footage even without an internet connection.
    """
    prompt = (
        "You are a financial knowledge graph construction model. I will provide a news article labeled INPUT.\n"
        "Your task is to extract triplets of the form [head:type, relation, tail:type, sector].\n"
        f"Entities must be one of: {ENTITY_TYPES}. Relationships must be one of: {BASE_RELATIONS}.\n"
        "First, summarize the document briefly. Then extract main triplets. Find the best suitable entity and relation types out of the allowed. Avoid redundant ones, simplify to most general form (e.g. 'foreign trage tarrifs' and 'international import tariffs' become 'import tariffs').\n"
        "Return ONLY valid JSON: a flat array of 4-element arrays like this:\n"
        '[["Apple Inc.:company", "acquisition", "Beats Electronics:company", "Technology"],\n'
        ' ["Google:company", "partnership", "OpenAI:company", "AI"]]\n'
        "Format: [exact_entity_name:type, relation, exact_entity_name:type, sector]\n"
        "Use exact names from text. Sector from context or null.\n"
        f"INPUT:\n{article_text}\n\nJSON:\n"
    )
    raw = generate(prompt, max_new_tokens=512)
    print(raw)
