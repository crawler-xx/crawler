#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import types
import urllib.request
import urllib.error
import json
import logging
import sqlite3

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(asctime)s %(filename)s %(funcName)s [line:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

RECORD_API_SERVER_URL = "http://record.boohee.com"
EATEINGS_HOT = "http://record.boohee.com/api/v2/eatings/hot?page={page}&token=wuCsg6pm9fnsvZj5P1Fm&user_key=c15fcaea-6010-4d70-8f09-2e1aad751859&app_version=5.9.2.3&app_device=Android&os_version=7.1.1&phone_model=XT1710-08&channel]"
THUMB_IMAGE_URL = "http://s2.boohee.cn{thumb_image_name}"
DB_NAME = "boohee.db"
DROP_TABLE_FOODS = '''DROP TABLE IF EXISTS "foods";'''
CREATE_TABLE_FOODS = '''
	CREATE TABLE "foods" (
	    "food_id" INTEGER NOT NULL,
	    "calory" REAL NOT NULL,
	    "weight" NULL NOT NULL,
	    "code" TEXT NOT NULL,
	    "name" TEXT NOT NULL,
	    "thumb_image_name" TEXT NOT NULL,
	    "health_light" INTEGER NOT NULL,
	    "is_liquid" INTEGER
);
'''
INSERT_TABLE_FOODS = '''
	insert into foods ("food_id", "calory", "weight", "code", "name", "thumb_image_name", "health_light", "is_liquid") 
	values (?, ?, ?, ?, ?, ?, ?, ?);
'''

def get_total_pages():
	try:
		url = EATEINGS_HOT.format(page = 1)
		json_data = urllib.request.urlopen(url).read()
		value = json.loads(json_data)
		total_pages = value["total_pages"]
		logging.info("total_pages = %s" % total_pages)
		return total_pages
	except Exception as e:
		print(e)
	else:
		pass
	finally:
		pass

def parse_record():
	# open db
	conn = sqlite3.connect(DB_NAME)
	cursor = conn.cursor()
	cursor.execute(DROP_TABLE_FOODS)
	cursor.execute(CREATE_TABLE_FOODS)
	# parser record
	total_pages = get_total_pages()
	num =  1
	data = []
	for page in xrange(1, total_pages):
		url = EATEINGS_HOT.format(page = page)
		json_data = urllib.request.urlopen(url).read()
		value = json.loads(json_data)
		foods = value["foods"]
		for food in foods:
			num +=  1
			thumb_image_url = THUMB_IMAGE_URL.format(thumb_image_name=food["thumb_image_name"])
			is_liquid = food["is_liquid"] and 1 or 0
			# ("food_id", "calory", "weight", "code", "name", "thumb_image_name", "health_light", "is_liquid") 
			data.append((int(food["food_id"]), float(food["calory"]), float(food["weight"]),
				food["code"], food["name"],  thumb_image_url,  int(food["health_light"]),is_liquid))
			# logging.info("-------------------------------------")
			# for key in food.keys():
			# 	logging.debug("%s:%s" % (key, food[key]))
			# logging.info("-------------------------------------")
	cursor.executemany(INSERT_TABLE_FOODS, data)	
	logging.debug("total foods = %d" % num)
	# close db
	conn.commit()
	conn.close()


def xrange(idx,x):
    n = idx
    while n < x:
        yield n
        n += 1

if __name__ == "__main__":
	parse_record()
