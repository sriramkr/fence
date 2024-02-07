import json
import urllib

import boto3
import openai
import base64
import requests

AUTH_URL = "http://localhost:8080/auth"
GATEWAY_URL = "http://localhost:8080/routes"
ACCESS_KEY_ID = "AKIAZI2LGNOM2PZBVP42"
SECRET_ACCESS_KEY = "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"

def get_identity_proof():
	# This is just for a test. In reality, we would absolutely not be checking in 
	# creds into the code.
	session = boto3.Session(
		aws_access_key_id=ACCESS_KEY_ID,
		aws_secret_access_key=SECRET_ACCESS_KEY,
	)
	# This is not the best way to provide identity proof, but it is good for an example.
	sts = session.client('sts'); 
	base_url = sts.generate_presigned_url(ClientMethod='get_caller_identity',Params={})
	return base_url

def get_api_key(identity_proof):
	r = requests.get(AUTH_URL, json={"idproof": identity_proof})
	resp = r.json()
	return resp['key']



#################
# Happy Path
#################
try:
	print("This is the happy path")
	# First get identity proof
	identity_proof = get_identity_proof()

	# Then exchange that for a fake API key
	api_key = get_api_key(identity_proof)

	# Set up an OpenAI client with this API key and base url set to our gateway.
	client = openai.OpenAI(api_key=api_key, base_url= GATEWAY_URL)

	# Now you can use the OpenAI client as you wish.
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
		{"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
		{"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
		])

	print(completion.choices[0].message)
	print("\n\n\n")
except:
	print("Happy path failed too, that's strange")

#################
# Unhappy paths
#################
print("Now for the unhappy paths:\n")

# 1. Try to get API key without proper identity proof 
try: 
	api_key = get_api_key("bad identity proof")
	print("This shouldn't have worked, something's wrong")
except:
	print("Getting API Key with bad identity proof failed, as expected")


# 2. Try to make a call with a forbidden word 
try: 
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
		{"role": "system", "content": "You are a passionfruit seller."},
		{"role": "user", "content": "Would you like some passionfruit?."}
		])

	print(completion.choices[0].message)
except:
	print("Making an OpenAI call with a forbidden word failed, as expected")