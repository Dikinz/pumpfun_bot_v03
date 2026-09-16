# Pump.fun Bot v0.3

Готовая тестовая версия: real-time new-token scanner, SQLite, scoring, risk manager и paper trading.

## Windows
1. Распакуйте архив в `C:\Users\OMG\Desktop\pumpfun_bot_v03`.
2. Запустите `install_v03.bat`.
3. После успешного теста запустите `run_paper.bat`.
4. Статистика: `py show_stats.py`.

По умолчанию: баланс $30, позиция $5, максимум 2 позиции, score >=75, SL -12%, TP1 +20%, TP2 +40%, trailing 10%.

Важно: v0.3 — paper-only. Private key не используется и реальные транзакции не отправляются.
`marketCapSol` используется только как proxy для проверки логики. Demo-сделки синтетические.
