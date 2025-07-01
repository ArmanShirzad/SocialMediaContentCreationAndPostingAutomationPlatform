# scheduler.py
import schedule
import time
import asyncio
from main import main as techcrunch_main

def job():
    asyncio.run(techcrunch_main())

schedule.every(6).hours.do(job)

if __name__ == "__main__":
    print("Scheduler started. The script will run every 6 hours.")
    while True:
        schedule.run_pending()
        time.sleep(1)
