# BikDesk — CONTEXT

> Последнее обновление: 2026-09-07

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| ED807-синк (src/sync.py) | готов, проверен на живых данных | 1398 участников, срез BusinessDay 2026-09-07 |
| Thin API (src/api.py) | каркас написан, не проверен | health / by BIC / search / dump |
| Юниты Sat (deploy/) | написаны, не выкладывались | sync.timer ~03:00 MSK, api :8789 |
| PG-база `banks` | не создана | ждёт решения о драйвере и деплоя |
| Репо GitHub | в работе | public, initial commit впереди |

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
