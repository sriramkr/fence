# fence
## PoC for API Security

This PoC sets up a very basic gateway at localhost:8080, and then shows how we can make OpenAI calls from a client go through this gateway with minimal interference. 
Once we have OpenAI calls going through our Gateway, we can do a bunch of things such as DLP, auditing, access control, etc.

To see it in action, first start the server and then start the client.

### Start the server
Go to `server` and run `go run server.go`. You might have to `go get` some packages first, based on the errors you see.

### Start the client
Once the server is running, in a new terminal, go to `client` and run `python3 client.py`. As with the server, you might have to `pip3 install` some packages when running for the first time.

### What's actually happening?

The client is using a standard OpenAI python client to make some calls to OpenAI. We have not interfered with the client at all.

Instead, we're using the `base_url` config option to make the client talk to our Gateway.

Also, we're not sharing the real OpenAI API key with the client. Instead, the client gets a fake API key from the Gateway. But even to get this fake key, the client has to pass some authz checks at the gateway first, which leverage AWS's `GetCallerIdentity` method.

Once the client gets this fake API key, it can use the standard OpenAI python library as desired. 

When the Gateway gets a OpenAI API call, it does a rudimentary DLP check. If the check passes, the Gateway replaces the fake API key with the real OpenAI API key and patches the call through. The client gets the expected response. If the check fails, the call is rejected.
