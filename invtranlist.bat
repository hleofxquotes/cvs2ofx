@echo off

cd C:\Users\hle\python\ofxlist-main

CALL .\venv\Scripts\activate
python src\invtranlist.py
CALL .\venv\Scripts\deactivate
