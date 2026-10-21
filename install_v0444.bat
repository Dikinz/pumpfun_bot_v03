@echo off
cd C:\Users\OMG\Desktop\pumpfun_bot_v04_4_4_cost_optimizer
py -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python -m pytest -q
pause
