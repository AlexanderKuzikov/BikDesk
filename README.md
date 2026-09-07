<p align="center">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white"></a>
  <a href="https://www.postgresql.org/"><img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-18-336791?logo=postgresql&logoColor=white"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/License-Apache_2.0-blue.svg"></a>
</p>

<h1 align="center">BikDesk</h1>
<p align="center">Справочник банков России: подстановка реквизитов по БИК из открытых данных ЦБ</p>

---

Ночной сбор ежедневного справочника БИК с cbr.ru (без ключей и аккаунтов) в базу на сервере. Другие приложения забирают реквизиты для платёжек и запросов о счетах контрагентов по тонкому HTTP API.

- **Открытые данные** — только ED807 с cbr.ru, ноль зависимостей в синке
- **Ночное обновление** — systemd-таймер, идемпотентно, с журналом изменений
- **Тонкий API** — реквизиты по БИК, поиск по названию, дамп среза
- **Веб-просмотр** — одна страница без сборки: поиск и сортировка по всем колонкам

## Быстрый старт

```bash
git clone https://github.com/AlexanderKuzikov/BikDesk.git
cd BikDesk
python src/sync.py --out data
python src/api.py --data data --port 8790
# фронт: http://127.0.0.1:8790/ — поиск и сортировка
curl "http://127.0.0.1:8790/api/banks/044525225"
```

## Документация

- [`docs/CONTEXT.md`](docs/CONTEXT.md) — состояние проекта
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — архитектурные решения

## Статус

**v0.3.0** — Развёрнуто на Sat: PG `banks`, ночной таймер, публичный фронт. Демо: https://bikdesk.135.106.192.125.nip.io/

## Лицензия

[Apache-2.0](LICENSE) © Alexander Kuzikov
