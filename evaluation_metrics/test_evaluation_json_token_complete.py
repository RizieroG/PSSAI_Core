# Valutazione su token "ufficiali" esportati da PSParser (JSON)

import argparse
import json
import re
import sys
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from nltk.metrics.distance import edit_distance
from rouge_score import rouge_scorer
from pathlib import Path
from sacrebleu.metrics import CHRF

# ---------------- Utils ----------------
def load_tokens(json_filepath: str):
    with open(json_filepath, 'r', encoding='utf-8-sig') as f:
        token_objs = json.load(f)
    # estrai solo il contenuto del token
    return [tok['Content'] for tok in token_objs]

def read_text(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def ensure_nltk():
    try:
        nltk.data.find('corpora/wordnet.zip')
        nltk.data.find('corpora/omw-1.4.zip')
    except LookupError:
        print("Download delle dipendenze NLTK (wordnet, omw-1.4)...")
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)

def safe_ratio(num, den):
    return (num / den) if den else 0.0

# helper per chrF
def tokens_to_string(tokens):
    """
    Concatena i token in una singola stringa separata da spazi.
    """
    return " ".join(tokens)

# -------------- Argparse ---------------
parser = argparse.ArgumentParser(description="Valuta coppia di script PowerShell usando token PSParser (JSON).")
parser.add_argument("--ref-ps1", type=str, default="example_519.ps1")
parser.add_argument("--cand-ps1", type=str, default="example_519_generated.ps1")
parser.add_argument("--ref-json", type=str, default=None, help="JSON token del ref; default = ref-ps1 con .json")
parser.add_argument("--cand-json", type=str, default=None, help="JSON token del cand; default = cand-ps1 con .json")
parser.add_argument("--csv-append", type=str, default=None, help="Se indicato, appende una riga CSV con i risultati")
parser.add_argument("--number", type=str, default="", help="Identificativo numerico (per CSV)")

args = parser.parse_args()

# Se non forniti, costruisci i cammini JSON sostituendo estensione
ref_json = args.ref_json or (str(Path(args.ref_ps1).with_suffix(".json")))
cand_json = args.cand_json or (str(Path(args.cand_ps1).with_suffix(".json")))

# --------- Caricamento file di codice ---------
try:
    reference_code = read_text(args.ref_ps1)
    candidate_code = read_text(args.cand_ps1)
except FileNotFoundError as e:
    print(f"ERRORE: file non trovato: {e.filename}")
    sys.exit(1)

print(f"✓ Riferimento: {args.ref_ps1}")
print(f"✓ Candidato:   {args.cand_ps1}")
print(f"✓ JSON ref:    {ref_json}")
print(f"✓ JSON cand:   {cand_json}")
print("-"*40)

# --------- Token dai JSON (PSParser) ----------
try:
    ref_tokens = load_tokens(ref_json)
    cand_tokens = load_tokens(cand_json)
except FileNotFoundError as e:
    print(f"ERRORE: JSON non trovato: {e.filename}")
    sys.exit(1)

list_of_ref_tokens = [ref_tokens]

# --------- NLTK deps ----------
ensure_nltk()

# --------- Metriche -----------
chencherry = SmoothingFunction()
bleu_1 = sentence_bleu(list_of_ref_tokens, cand_tokens, weights=(1,0,0,0), smoothing_function=chencherry.method1)
bleu_2 = sentence_bleu(list_of_ref_tokens, cand_tokens, weights=(0.5,0.5,0,0), smoothing_function=chencherry.method1)
bleu_4 = sentence_bleu(list_of_ref_tokens, cand_tokens, smoothing_function=chencherry.method1)

rouge_calc = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
rouge_scores = rouge_calc.score(reference_code, candidate_code)
rougeL_f = rouge_scores['rougeL'].fmeasure
rougeL_precision = rouge_scores['rougeL'].precision
rougeL_recall = rouge_scores['rougeL'].recall

meteor = meteor_score(list_of_ref_tokens, cand_tokens)

edit_raw = edit_distance(ref_tokens, cand_tokens)
edit_norm = safe_ratio(edit_raw, max(len(ref_tokens), len(cand_tokens)))

# chrF necessita di stringhe
ref_str = tokens_to_string(ref_tokens)
cand_str = tokens_to_string(cand_tokens)

# chrF corpus-level con default: char_order=6, word_order=0
chrf_metric = CHRF(char_order=6, word_order=0)
chrf_score_obj = chrf_metric.corpus_score([cand_str], [[ref_str]])
chrf_score = chrf_score_obj.score
chrf_signature = chrf_metric.get_signature()

# --------- Stampa risultati ----------
print(f"BLEU-1:    {bleu_1:.4f}")
print(f"BLEU-2:    {bleu_2:.4f}")
print(f"BLEU-4:    {bleu_4:.4f}")
print(f"ROUGE-L P: {rougeL_precision:.4f}")
print(f"ROUGE-L R: {rougeL_recall:.4f}")
print(f"ROUGE-L F: {rougeL_f:.4f}")
print(f"METEOR:    {meteor:.4f}")
print(f"EditDist:  {edit_raw}  (norm={edit_norm:.4f})")
print(f"chrF:      {chrf_score:.4f}")
print(f"chrF sig:  {chrf_signature}")
print("-"*40)

# --------- CSV opzionale ----------
if args.csv_append:
    line = (
        f"{args.number},{args.ref_ps1},{args.cand_ps1},"
        f"{bleu_1:.6f},{bleu_2:.6f},{bleu_4:.6f},"
        f"{rougeL_f:.6f},{meteor:.6f},{edit_raw},{edit_norm:.6f},"
        f"{chrf_score:.6f}\n"
    )
    # crea file se non esiste
    p = Path(args.csv_append)
    if not p.exists():
        p.write_text(
            "number,ref_ps1,cand_ps1,BLEU1,BLEU2,BLEU4,ROUGE_L_F,METEOR,EditDistance,EditNorm,chrF\n",
            encoding="utf-8"
        )
    with open(p, "a", encoding="utf-8") as f:
        f.write(line)
