"""BikDesk nightly sync: ED807 from cbr.ru -> banks.jsonl (+ optional PG upsert).

Stdlib only (PG needs psycopg only when --pg is used).
Schema source of truth: live ED807, windows-1251, ns urn:cbr-ru:ed:v2.0.
Raw CBR codes are stored as-is, never interpreted here.

Usage:
    python src/sync.py --out data
    python src/sync.py --out data --check
    python src/sync.py --out data --pg postgresql://user:pass@localhost:5432/banks
"""

import argparse
import datetime as dt
import io
import json
import os
import sys
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

SOURCE_URL = "https://www.cbr.ru/s/newbik"
USER_AGENT = "BikDesk/0.1"
NS = {"e": "urn:cbr-ru:ed:v2.0"}
MIN_ENTRIES = 1000  # anomaly guard: real directory is ~1400 rows

# Runnable self-check: BIC -> expected active corr account (verified 2026-09-07).
SPOT_CHECKS = {
    "044525225": "30101810400000000225",  # Sberbank
}


def fetch_archive(url=SOURCE_URL):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def extract_ed807(archive):
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        names = [n for n in z.namelist() if "ED807" in n and n.endswith(".xml")]
        if not names:
            raise ValueError(f"no ED807 xml in archive: {z.namelist()}")
        return z.read(sorted(names)[0]).decode("windows-1251")


def parse_records(xml_text):
    root = ET.fromstring(xml_text)
    meta = {
        "business_day": root.get("BusinessDay"),
        "ed_no": root.get("EDNo"),
        "ed_date": root.get("EDDate"),
    }
    records = []
    for entry in root.findall("e:BICDirectoryEntry", NS):
        bic = entry.get("BIC")
        pi = entry.find("e:ParticipantInfo", NS)
        if pi is None:
            continue
        accounts = [
            {
                "account": a.get("Account"),
                "type": a.get("RegulationAccountType"),
                "status": a.get("AccountStatus"),
                "cbr_bic": a.get("AccountCBRBIC"),
                "date_in": a.get("DateIn"),
            }
            for a in entry.findall("e:Accounts", NS)
        ]
        active = next((a for a in accounts if a["status"] == "ACAC"), None)
        corr = (active or (accounts[0] if accounts else {})).get("account")
        addr = ", ".join(
            p for p in [
                pi.get("Ind"),
                " ".join(p for p in [pi.get("Tnp"), pi.get("Nnp")] if p),
                pi.get("Adr"),
            ] if p
        )
        records.append({
            "bic": bic,
            "name": pi.get("NameP"),
            "name_en": pi.get("EnglName"),
            "reg_n": pi.get("RegN"),
            "corr_account": corr,
            "accounts": accounts,
            "participant_status": pi.get("ParticipantStatus"),
            "pt_type": pi.get("PtType"),
            "region": pi.get("Rgn"),
            "address": addr or None,
            "parent_bic": pi.get("PrntBIC"),
            "date_in": pi.get("DateIn"),
            "uid": pi.get("UID"),
        })
    records.sort(key=lambda r: r["bic"] or "")
    return meta, records


def write_snapshot(out_dir, meta, records):
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "banks.jsonl", "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    full_meta = {
        **meta,
        "entries": len(records),
        "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    with open(out_dir / "banks.meta.json", "w", encoding="utf-8") as f:
        json.dump(full_meta, f, ensure_ascii=False, indent=2)
    return full_meta


def run_checks(records):
    if len(records) < MIN_ENTRIES:
        raise AssertionError(f"entries {len(records)} < guard {MIN_ENTRIES}")
    by_bic = {r["bic"]: r for r in records}
    for bic, account in SPOT_CHECKS.items():
        rec = by_bic.get(bic)
        if rec is None:
            raise AssertionError(f"spot BIC {bic} missing")
        if rec["corr_account"] != account:
            raise AssertionError(f"spot BIC {bic}: corr {rec['corr_account']} != {account}")
        if not rec["name"]:
            raise AssertionError(f"spot BIC {bic}: empty name")
    for bic in ("044525187", "044525593"):  # VTB, Alfa — presence only
        if bic not in by_bic:
            raise AssertionError(f"expected BIC {bic} missing")
    print(f"CHECK OK: {len(records)} entries, spot checks passed")


DDL = """
CREATE TABLE IF NOT EXISTS banks (
    bic TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS bank_changes (
    id BIGSERIAL PRIMARY KEY,
    changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    bic TEXT NOT NULL,
    field TEXT NOT NULL,
    old_val TEXT,
    new_val TEXT
);
"""

TRACKED = ("name", "corr_account", "participant_status", "reg_n", "parent_bic")


def upsert_pg(dsn, records):
    try:
        import psycopg
    except ImportError:
        sys.exit("psycopg is not installed; run without --pg for JSONL-only mode")
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(DDL)
            cur.execute("SELECT bic, data FROM banks")
            old = {bic: data for bic, data in cur.fetchall()}
            now_new = {r["bic"]: r for r in records}
            for bic, rec in now_new.items():
                prev = old.get(bic)
                cur.execute(
                    "INSERT INTO banks (bic, data) VALUES (%s, %s) "
                    "ON CONFLICT (bic) DO UPDATE SET data = EXCLUDED.data, "
                    "updated_at = now() WHERE banks.data IS DISTINCT FROM EXCLUDED.data",
                    (bic, json.dumps(rec, ensure_ascii=False)),
                )
                if prev:
                    for field in TRACKED:
                        o, n = prev.get(field), rec.get(field)
                        if o != n:
                            cur.execute(
                                "INSERT INTO bank_changes (bic, field, old_val, new_val)"
                                " VALUES (%s, %s, %s, %s)",
                                (bic, field, None if o is None else str(o),
                                 None if n is None else str(n)),
                            )
                else:
                    cur.execute(
                        "INSERT INTO bank_changes (bic, field, old_val, new_val)"
                        " VALUES (%s, %s, NULL, %s)",
                        (bic, "bic", f"new:{rec.get('name')}"),
                    )
            for bic in old:
                if bic not in now_new:
                    cur.execute(
                        "DELETE FROM banks WHERE bic = %s", (bic,)
                    )
                    cur.execute(
                        "INSERT INTO bank_changes (bic, field, old_val, new_val)"
                        " VALUES (%s, %s, %s, NULL)",
                        (bic, "bic", f"dropped:{(old[bic] or {}).get('name')}"),
                    )
        conn.commit()
    print(f"PG OK: {len(records)} upserted")


def main():
    from pathlib import Path
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--pg", default=os.environ.get("DATABASE_URL"))
    args = ap.parse_args()

    out_dir = Path(args.out)
    meta_file = out_dir / "banks.meta.json"
    archive = fetch_archive()
    xml_text = extract_ed807(archive)
    meta, records = parse_records(xml_text)
    if len(records) < MIN_ENTRIES:
        sys.exit(f"ANOMALY: only {len(records)} entries, refusing to write (use --force to override)"
                 if not args.force else f"WARNING: only {len(records)} entries, forced")
    if meta_file.exists() and not args.force:
        prev_day = json.loads(meta_file.read_text(encoding="utf-8")).get("business_day")
        if prev_day == meta["business_day"]:
            print(f"SKIP: BusinessDay {meta['business_day']} already stored")
            if args.check:
                old = [json.loads(l) for l in
                       (out_dir / "banks.jsonl").read_text(encoding="utf-8").splitlines()]
                run_checks(old)
            return
    full_meta = write_snapshot(out_dir, meta, records)
    print(f"WROTE: {full_meta['entries']} entries, BusinessDay {full_meta['business_day']}")
    if args.check:
        run_checks(records)
    if args.pg:
        upsert_pg(args.pg, records)


if __name__ == "__main__":
    main()
