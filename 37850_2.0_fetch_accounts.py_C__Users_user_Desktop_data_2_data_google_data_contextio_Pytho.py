import helpers
import contextio as c

CONSUMER_KEY = "YOUR_CONTEXTIO_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONTEXTIO_CONSUMER_KEY"

api = c.ContextIO(
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    debug=True
) # returns v2.0 API by default

helpers.headerprint("FETCHING ACCOUNTS (v2.0 API)")

accounts = api.get_accounts()

print accounts
print "\n"
print "Found {0} accounts.".format(len(accounts))
print "\n"
