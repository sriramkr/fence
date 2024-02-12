import json
import urllib

import boto3
import openai
import base64
import requests
from http.client import HTTPConnection
import logging
import sys
import httpx
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
formatter = logging.Formatter(fmt="%(name)s %(funcName)s %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# def safe_call(func):
# 	real_putrequest = HTTPConnection.putrequest

# 	def new_putrequest(self, method, url, skip_host=False, skip_accept_encoding=False):
# 		print(f'{method}: {url}')
# 		logger.info("calling with wrapper")
# 		real_putrequest(self, method, url, skip_host=skip_host, skip_accept_encoding=skip_accept_encoding)


# 	def wrapper(*args, **kwargs):
# 		logger.info("calling with wrapper")
# 		HTTPConnection.putrequest = new_putrequest
# 		return func(*args, **kwargs)
# 	return wrapper

oldrequest = httpx.Client.request

def new_request(*args, **kwargs):
	print("This works4???")
	return oldrequest(args, kwargs)

httpx.Client.request = new_request

oldget = httpx.Client.get

def new_get(*args, **kwargs):
	print("This works3???")
	return oldget(args, kwargs)

httpx.Client.get = new_get


oldpost = httpx.Client.post

def new_post(*args, **kwargs):
	print("This works2???")
	return oldpost(args, kwargs)

httpx.Client.post = new_post

oldsend = httpx.Client.send

def new_send(*args, **kwargs):
	print("This works1???")
	return oldsend(*args, **kwargs)

httpx.Client.send = new_send



def call_openai(message):
	client = openai.OpenAI(api_key="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")
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
		{"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
		{"role": "user", "content": message}
		])

	return completion.choices[0].message

message = "Compose a poem that explains the concept of recursion in programming."
print(call_openai(message))
