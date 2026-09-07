# BikDesk — Instructions for AI Agents

## Commands
- sync: `python src/sync.py --out data`
- sync check: `python src/sync.py --out data --check`
- api: `python src/api.py --data data --port 8790`
- no tests yet (single runnable check inside sync.py)

## Conventions
- Python, stdlib only in `src/` (urllib, zipfile, xml, http.server). No pip installs without explicit user approval.
- Python вызывается как `python`, не `python3`.
- Source of truth for schema: live ED807 from cbr.ru, encoding windows-1251, namespace `urn:cbr-ru:ed:v2.0`.
- Raw CBR codes (PtType, ParticipantStatus, AccountStatus) stored as-is; no invented mappings.
- OS target: Ubuntu Noble on Sat; local dev on Windows 11.

## Structure
- `src/sync.py` — nightly ED807 download → `banks.jsonl` + `banks.meta.json`, optional PG upsert
- `src/api.py` — thin read-only HTTP API (health, by BIC, search, dump)
- `deploy/` — systemd units + Caddy snippet for Sat
- `data/` — local snapshots, gitignored, never committed

## Do NOT touch
- `C:\Users\alexa\AppData\Local\hermes\` — чужой агент, не трогать
- Sat server (`135.106.192.125`) — только по явной просьбе на деплой
- `git push --force`, `git reset --hard` — только с подтверждением
- Commit + push — только когда явно попросят

## Git
- Один коммит на одну задачу, не десятки в день
- Заголовок = строка из журнала docs/CONTEXT.md («коммит = строка журнала»)
- Промежуточные сохранения — локально с `wip`, перед пушем squash в один осмысленный

## Documentation rules
- После работы — обнови docs/CONTEXT.md
- Если принял архитектурное решение — запиши в docs/DECISIONS.md
- НЕ создавай новых файлов документации без разрешения
- Переиспользуемые знания — в D:\GitHub\knowledge/README.md
