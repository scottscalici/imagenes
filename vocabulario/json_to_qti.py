import json, os, random, zipfile
from lxml import etree

INPUT_FILE = "desc3lec4.json"
OUTPUT_DIR = "qti_output"
ZIP_NAME = "qti_vocab_quiz.zip"

# === SETTINGS ===
TARGET_LECCION = "4.1"  # Change this to 4.2, 4.3, etc.

# === Article and Adjective helpers ===
ARTICLES = ["el", "la", "los", "las"]

def strip_article(word):
    parts = word.split()
    return " ".join(p for p in parts if p.lower() not in ARTICLES)

def get_adjective_forms(adj):
    # crude expansion for adjectives ending in -o/-a
    base = adj.rstrip("ao")
    return {f"{base}o", f"{base}a", f"{base}os", f"{base}as"}

def normalize_answer(word):
    word = strip_article(word)
    if "/" in word:  # e.g. médico/a
        stem, endings = word.split("/")[0], word.split("/")[1:]
        return {stem + e for e in ["o", "a", "os", "as"]}
    if word.endswith(("o", "a")):
        return get_adjective_forms(word)
    return {word}

# === QTI GENERATOR ===
def create_qti_question(qid, prompt, correct, distractors):
    root = etree.Element("item", ident=qid, title=f"Vocab Q{qid}")
    
    presentation = etree.SubElement(root, "presentation")
    material = etree.SubElement(presentation, "material")
    etree.SubElement(material, "mattext", texttype="text").text = prompt

    response_lid = etree.SubElement(presentation, "response_lid", ident="response1", rcardinality="Single")
    render_choice = etree.SubElement(response_lid, "render_choice")

    choices = distractors + [correct]
    random.shuffle(choices)
    correct_id = f"choice{choices.index(correct)}"

    for i, choice in enumerate(choices):
        label = etree.SubElement(render_choice, "response_label", ident=f"choice{i}")
        mat = etree.SubElement(label, "material")
        etree.SubElement(mat, "mattext", texttype="text").text = choice

    resprocessing = etree.SubElement(root, "resprocessing")
    outcomes = etree.SubElement(resprocessing, "outcomes")
    etree.SubElement(outcomes, "decvar", varname="SCORE", vartype="Decimal", defaultval="0")

    respcond = etree.SubElement(resprocessing, "respcondition", title="correct")
    condvar = etree.SubElement(respcond, "conditionvar")
    etree.SubElement(condvar, "varequal", respident="response1").text = correct_id
    etree.SubElement(respcond, "setvar", action="Set").text = "1"

    return etree.tostring(root, pretty_print=True, encoding="UTF-8", xml_declaration=True)

# === MAIN FUNCTION ===
def generate_qti():
    with open(INPUT_FILE, encoding="utf-8") as f:
        data = json.load(f)

    vocab = [entry for entry in data if entry.get("evaluacion") and entry.get("leccion") == TARGET_LECCION]

    if not vocab:
        print("No vocab found for selected lesson.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, entry in enumerate(vocab):
        prompt = entry["definicion"]
        correct_raw = entry["palabra"]
        correct_forms = list(normalize_answer(correct_raw))
        correct_choice = correct_forms[0]

        # Get distractors
        distractor_pool = [e["palabra"] for e in vocab if e["palabra"] != correct_raw]
        distractors = random.sample([strip_article(d) for d in distractor_pool], k=3)

        qti_xml = create_qti_question(f"q{i+1}", prompt, correct_choice, distractors)

        with open(os.path.join(OUTPUT_DIR, f"q{i+1}.xml"), "wb") as out:
            out.write(qti_xml)

    # Zip it
    with zipfile.ZipFile(ZIP_NAME, "w") as zipf:
        for fname in os.listdir(OUTPUT_DIR):
            zipf.write(os.path.join(OUTPUT_DIR, fname), fname)

    print(f"QTI quiz created: {ZIP_NAME}")

if __name__ == "__main__":
    generate_qti()
