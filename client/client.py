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
BAD_USER_ACCESS_KEY_ID = "AKIAZI2LGNOMUFYEFJAM"
BAD_USER_SECRET_ACCESS_KEY = "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"

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


def happy_path():
	try:
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

		if completion.choices[0].message:
			return True
		else:
			return False
	except:
		return False


def bad_id_proof():
	try: 
		api_key = get_api_key("bad identity proof")
		return False
	except:
		return True


def forbidden_word():
	try: 
		identity_proof = get_identity_proof()
		api_key = get_api_key(identity_proof)
		client = openai.OpenAI(api_key=api_key, base_url= GATEWAY_URL)
		completion = client.chat.completions.create(
			model="gpt-3.5-turbo",
			messages=[
			{"role": "system", "content": "You are a passionfruit seller."},
			{"role": "user", "content": "Would you like some passionfruit?."}
			])
		if completion.choices[0].message:
			return False
		else:
			return True
	except:
		return True

def bad_user():
	try: 
		bad_session = boto3.Session(
			aws_access_key_id=BAD_USER_ACCESS_KEY_ID,
			aws_secret_access_key=BAD_USER_SECRET_ACCESS_KEY,
		)
		sts = bad_session.client('sts'); 
		base_url = sts.generate_presigned_url(ClientMethod='get_caller_identity',Params={})
		r = requests.get(AUTH_URL, json={"idproof": base_url})
		resp = r.json()
		if resp['key']:
			return False
		else:
			return True
	except:
			return True


def main():
	print ("Happy Path: ", "Passed" if happy_path() else "Failed")
	print ("AuthN Checks: ", "Passed" if bad_id_proof() else "Failed")
	print ("AuthZ Checks: ", "Passed" if bad_user() else "Failed")
	print ("DLP Checks: ", "Passed" if forbidden_word() else "Failed")


if __name__ == "__main__":
    main()

