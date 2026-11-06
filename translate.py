import pandas as pd
from deep_translator import GoogleTranslator

# Input and output file paths
input_path = "scraped_files/la-vista.csv"       # your original file
output_path = "scraped_files/translated-la-vista.csv"  # file with translations

# --- Step 1: Load CSV safely ---
try:
    df = pd.read_csv(input_path, encoding="utf-8")
    print("✅ Read file as UTF-8")
except UnicodeDecodeError:
    df = pd.read_csv(input_path, encoding="cp1252")
    print("✅ Read file as CP1252 (Windows Latin-1)")

# --- Step 2: Fix encoding errors in text ---
def fix_encoding(text):
    """Repair common UTF-8/Latin-1 garbling like 'fÃ¡cil' -> 'fácil'."""
    if isinstance(text, str):
        try:
            return text.encode("latin-1").decode("utf-8")
        except Exception:
            return text
    return text

df["Content"] = df["Content"].apply(fix_encoding)
df["Title"] = df["Title"].apply(fix_encoding)

# --- Step 3: Translator setup ---
translator = GoogleTranslator(source="es", target="en")

def chunk_text(text, max_chars=4500):
    """Split text into chunks at word boundaries (safe for Google Translate)."""
    words = text.split()
    chunks, current_chunk = [], ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_chars:
            current_chunk += (" " if current_chunk else "") + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def safe_translate(text):
    """Translate Spanish text into English safely with chunking."""
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        chunks = chunk_text(text)
        translated_chunks = [translator.translate(chunk) for chunk in chunks]
        return " ".join(translated_chunks)
    except Exception as e:
        print(f"⚠️ Translation error: {e}")
        return text  # fallback: keep original Spanish

# --- Step 4: Translate with counter ---
print("🚀 Starting translation...")

translated_content = []
translated_titles = []
total_rows = len(df)

for i, (title, content) in enumerate(zip(df["Title"], df["Content"]), start=1):
    translated_title = safe_translate(title)
    translated_content_text = safe_translate(content)

    translated_titles.append(translated_title)
    translated_content.append(translated_content_text)

    print(f"✅ Translated {i}/{total_rows}")

df["English_Title"] = translated_titles
df["Translated_Content"] = translated_content

# --- Step 5: Save clean CSV ---
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"🎉 All {total_rows} articles translated! File saved as: {output_path}")
