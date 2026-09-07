# BikDesk — CONTEXT

> Последнее обновление: 2026-09-07

## Статус
| Компонент | Статус | Версия/Заметка |
|-----------|--------|----------------|
| ED807-синк (src/sync.py) | готов, проверен на живых данных | 1398 участников, срез BusinessDay 2026-09-07 |
| Thin API (src/api.py) | готов, проверен локально | health / by BIC / search / dump + раздаёт фронт |
| Веб-просмотр (web/index.html) | готов, проверен локально | одна страница без сборки: поиск, сортировка по колонкам |
| Юниты Sat (deploy/) | написаны, не выкладывались | sync.timer ~03:00 MSK, api :8789, Caddy — один reverse_proxy на всё |
| PG-база `banks` | не создана | образ postgres:18-alpine, отдельная БД в существующем кластере Sat |
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
| 2026-09-07 | Синк и API проверены на живых данных ЦБ (1398 записей, BusinessDay 2026-09-07); public-репо создан и запушен |
| 2026-09-07 | PG 18.6 — последняя стабильная (19 только Beta 3); описание репо на русском; веб-просмотр + раздача фронта через api.py, проверено локально |

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
