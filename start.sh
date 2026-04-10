#!/bin/bash
cd /Users/jeinyu/Dev/tv_remote/server
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
