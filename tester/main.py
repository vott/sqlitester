import asyncio
import argparse
import crawler
import datetime

import motor.motor_asyncio

from crawler import SeleniumCrawler

async def do_insert(db):
        document = {'url':'http://www.google.com', 'date': datetime.datetime.utcnow()}
        result = await db.url.insert_one(document)
        print('result %s' % repr(result.inserted_id))

def main():
    """
    Tester entry point
    """
    client = motor.motor_asyncio.AsyncIOMotorClient('mongodb', 27017)
    db = client['tester']
    collection = db['urls']
    loop = asyncio.get_event_loop()
    print(loop.run_until_complete(do_insert(db)))
    parser = argparse.ArgumentParser()
    crawler = SeleniumCrawler('http://0.0.0.0/', [], 'login.php')


if __name__ == "__main__":
    main()