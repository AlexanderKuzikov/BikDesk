# BikDesk — CONTEXT

> Последнее обновление: 2026-09-07

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| ED807-синк (src/sync.py) | на Sat, timer 03:10 MSK | PG-апдейт идёт и при SKIP, venv + .env |
| Thin API (src/api.py) | на Sat, active :8790 | https://bikdesk.135.106.192.125.nip.io/ |
| Веб-просмотр (web/index.html) | public, проверен снаружи | отдаётся с того же поддомена |
| Юниты Sat (deploy/) | установлены и enabled | sync.timer next run 2026-09-08, api active |
| PG-база `banks` | готова, 1398 строк | postgres:18-alpine, роль bikdesk, пароль в .env 600 |
| Репо GitHub | в работе | public |

## Open-проблемы
| # | Priority | Описание |
|---|----------|----------|
| 1 | high | Маппинги кодов PtType / ParticipantStatus / AccountStatus сверить с альбомом УФЭБС — пока храним сырые коды, не интерпретируем |
| 2 | high | PG-драйвер (psycopg) требует pip install на Sat — нужно явное разрешение пользователя |
| 3 | medium | Деплой на Sat (systemd + Caddy + база) — только по просьбе, сервер руками не трогать |
| 4 | low | История исключённых участников копится только с первого синка — ретроспективы отзывов нет |

## Журнал работ
| Дата | Изменение |
|------|-----------|
| 2026-09-07 | Создан каркас BikDesk: README, AGENTS, docs, sync.py, api.py, deploy-юниты |
| 2026-09-07 | Синк и API проверены на живых данных ЦБ (1398 записей, BusinessDay 2026-09-07); public-репо создан и запушен |
| 2026-09-07 | PG 18.6 — последняя стабильная (19 только Beta 3); описание репо на русском; веб-просмотр + раздача фронта через api.py, проверено локально |
| 2026-09-07 | Порт сменён 8789→8790 (конфликт со StatGladys), сниппет в домашнем стиле, ADR про порт и отсутствие auth |
| 2026-09-07 | Деплой на Sat: venv+psycopg 3.3.5, роль/БД banks, первый синк (1398), юниты enabled, Caddy-поддомен с LE, фронт public |

## Структура проекта
```
BikDesk/
├── README.md
├── AGENTS.md
├── LICENSE
├── src/
│   ├── sync.py     # ED807 → banks.jsonl (+PG upsert при наличии драйвера)
│   └── api.py      # thin read-only HTTP API
├── deploy/
│   ├── bikdesk-sync.service
│   ├── bikdesk-sync.timer
│   ├── bikdesk-api.service
│   └── caddy-snippet.conf
└── docs/
    ├── CONTEXT.md
    └── DECISIONS.md
```
