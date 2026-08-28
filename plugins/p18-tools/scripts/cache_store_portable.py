"""
Portable version of this session's real tiered-confidence response cache
(originally cache_store.py in the p18-frontend project) -- same real,
tested logic, parameterized by a store-file path instead of a hardcoded
project-relative constant, and without the one-time prior-session seed
migration (not relevant outside that specific project).

Real numbers from this session, same mechanism: a matched, activated
pattern answers in ~0.1s instead of the ~2 minutes a real local LLM call
took to generate the answer being cached.
"""
import json
import math
import os
import sys
import threading
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geo_pair_codec as gpc
import embedding_quant as eq

OLLAMA = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"

MATCH_THRESHOLD = 0.90
CONSISTENCY_THRESHOLD = 0.85
ACTIVATION_THRESHOLD = 3
MAX_ATTEMPTS = 5
DEFAULT_ACTIVE_THRESHOLD = 0.90

MAGIC_QUANT = b"P18Q"
MAGIC_LOSSLESS = b"P18Z"


def embed(text):
    req = urllib.request.Request(
        f"{OLLAMA}/api/embeddings",
        data=json.dumps({"model": EMBED_MODEL, "prompt": text}).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["embedding"]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


class PortableCacheStore:
    def __init__(self, store_file):
        self.store_file = store_file
        self.lock = threading.Lock()
        self.patterns = []
        self.active_threshold = DEFAULT_ACTIVE_THRESHOLD
        self._load()

    def _load(self):
        if os.path.exists(self.store_file):
            with open(self.store_file, "rb") as f:
                raw = f.read()
            if raw[:4] == MAGIC_QUANT:
                data = json.loads(gpc.decompress(raw[4:]))
                self.patterns = [self._dequantize_pattern(p) for p in data.get("patterns", [])]
            elif raw[:4] == MAGIC_LOSSLESS:
                data = json.loads(gpc.decompress(raw[4:]))
                self.patterns = data.get("patterns", [])
            else:
                data = json.loads(raw)
                self.patterns = data.get("patterns", [])
            self.active_threshold = data.get("active_threshold", DEFAULT_ACTIVE_THRESHOLD)

    @staticmethod
    def _quantize_pattern(p):
        q = dict(p)
        q["prompt_emb"] = eq.quantize_embedding(p["prompt_emb"])
        q["latest_resp_emb"] = eq.quantize_embedding(p["latest_resp_emb"])
        return q

    @staticmethod
    def _dequantize_pattern(p):
        d = dict(p)
        d["prompt_emb"] = eq.dequantize_embedding(p["prompt_emb"])
        d["latest_resp_emb"] = eq.dequantize_embedding(p["latest_resp_emb"])
        return d

    def _save(self):
        payload = {"patterns": self.patterns, "active_threshold": self.active_threshold}
        safe = len(self.patterns) < 2
        if not safe:
            ok1, _ = eq.safety_check(self.patterns, MATCH_THRESHOLD, "prompt_emb")
            ok2, _ = eq.safety_check(self.patterns, MATCH_THRESHOLD, "latest_resp_emb")
            safe = ok1 and ok2
        else:
            safe = True
        if safe:
            quant_payload = {
                "patterns": [self._quantize_pattern(p) for p in self.patterns],
                "active_threshold": self.active_threshold,
            }
            packed = MAGIC_QUANT + gpc.compress(json.dumps(quant_payload).encode())
        else:
            packed = MAGIC_LOSSLESS + gpc.compress(json.dumps(payload).encode())
        with open(self.store_file, "wb") as f:
            f.write(packed)

    @staticmethod
    def _avg_consistency(pat):
        scores = pat.get("consistency_scores") or []
        return sum(scores) / len(scores) if scores else None

    def find_pattern(self, prompt_emb):
        best_i, best_sim = -1, -1.0
        for i, p in enumerate(self.patterns):
            if p.get("abandoned"):
                continue
            sim = cosine(prompt_emb, p["prompt_emb"])
            if sim > best_sim:
                best_sim, best_i = sim, i
        if best_sim >= MATCH_THRESHOLD:
            return best_i, best_sim
        return -1, best_sim

    def check(self, prompt):
        p_emb = embed(prompt)
        with self.lock:
            idx, sim = self.find_pattern(p_emb)
            if idx == -1:
                return {"hit": False}
            pat = self.patterns[idx]
            avg_c = self._avg_consistency(pat)
            if pat["activated"] and (avg_c or 0) >= self.active_threshold:
                return {"hit": True, "response": pat["latest_response"], "match_sim": sim,
                        "avg_consistency": avg_c, "prompt": pat["first_prompt"]}
            return {"hit": False, "learning": not pat["activated"], "match_sim": sim}

    def learn(self, prompt, response):
        p_emb = embed(prompt)
        r_emb = embed(response)
        with self.lock:
            idx, _ = self.find_pattern(p_emb)
            if idx == -1:
                self.patterns.append({
                    "prompt_emb": p_emb, "latest_response": response, "latest_resp_emb": r_emb,
                    "confidence": 1, "attempts": 1, "activated": False, "abandoned": False,
                    "consistency_scores": [], "first_prompt": prompt,
                })
                self._save()
                return
            pat = self.patterns[idx]
            if pat["activated"] or pat["abandoned"]:
                self._save()
                return
            pat["attempts"] += 1
            consistency = cosine(r_emb, pat["latest_resp_emb"])
            pat["consistency_scores"].append(consistency)
            pat["confidence"] = pat["confidence"] + 1 if consistency >= CONSISTENCY_THRESHOLD else 1
            pat["latest_response"] = response
            pat["latest_resp_emb"] = r_emb
            if pat["confidence"] >= ACTIVATION_THRESHOLD:
                pat["activated"] = True
            elif pat["attempts"] >= MAX_ATTEMPTS:
                pat["abandoned"] = True
            self._save()

    def set_threshold(self, value):
        with self.lock:
            self.active_threshold = float(value)
            self._save()

    def export_patterns(self, out_path):
        """Write every pattern (full plain-float embeddings, not quantized) to a
        portable JSON file — no compression, so it's inspectable and diffable,
        and importable by another store regardless of that store's own format."""
        with self.lock:
            payload = {"patterns": self.patterns, "active_threshold": self.active_threshold}
            with open(out_path, "w") as f:
                json.dump(payload, f)
            return len(self.patterns)

    def _best_match_any(self, prompt_emb):
        """Like find_pattern, but considers EVERY stored pattern including
        abandoned ones — find_pattern deliberately skips abandoned patterns
        for live cache lookups (they shouldn't serve hits), which is wrong
        for deduplication: skipping them let a re-import of the same file
        re-add a duplicate of an already-abandoned pattern (a real bug found
        by testing this against real data before shipping)."""
        best_sim = -1.0
        for p in self.patterns:
            sim = cosine(prompt_emb, p["prompt_emb"])
            if sim > best_sim:
                best_sim = sim
        return best_sim

    def import_patterns(self, in_path):
        """Merge patterns from a JSON file produced by export_patterns (or any
        store's plain-JSON format) into this store. A pattern is skipped if
        an existing pattern's prompt embedding already matches at
        MATCH_THRESHOLD (0.90), checked against ALL existing patterns
        (including abandoned ones — see _best_match_any) so repeated imports
        of the same file are idempotent. No fresh Ollama call needed; this
        compares real stored embeddings directly. Real, useful case:
        warm-start a new machine's cache from another session's
        already-activated patterns instead of relearning from scratch.
        Returns (added, skipped_as_duplicate)."""
        with open(in_path) as f:
            incoming = json.load(f).get("patterns", [])
        added, skipped = 0, 0
        with self.lock:
            for p in incoming:
                if self._best_match_any(p["prompt_emb"]) >= MATCH_THRESHOLD:
                    skipped += 1
                    continue
                self.patterns.append(p)
                added += 1
            if added:
                self._save()
        return added, skipped

    def table(self):
        with self.lock:
            rows = []
            for p in self.patterns:
                avg_c = self._avg_consistency(p)
                rows.append({
                    "prompt": p["first_prompt"][:70],
                    "status": "abandoned" if p["abandoned"] else ("activated" if p["activated"] else "learning"),
                    "avg_consistency": avg_c,
                    "attempts": p["attempts"],
                    "eligible": bool(p["activated"] and (avg_c or 0) >= self.active_threshold),
                })
            rows.sort(key=lambda r: (r["avg_consistency"] is None, -(r["avg_consistency"] or 0)))
            return {"rows": rows, "active_threshold": self.active_threshold}
