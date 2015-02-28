#################################
#
# TequilaMockingbird is a Python script that tweets
# when new items are downloaded by Reposado.
#
# Largely based on the TweetCatalogUpdates script.
#
# Written by Tim Schutt - taschutt@syr.edu
#
# March, 2015
#
#################################

import os, plistlib, datetime, sys, shutil, hashlib, tweepy

#========== Modify to match your environment ===========#

### Reposado root directory (showing html and metadata directories) ###
reposado_root = "/Volumes/reposado"

### Twitter Consumer API key & token, and Access token & secret ###
ckey = ''
csecret = ''
atok = ''
asecret = ''

### Set armed to True to send tweets.
### Otherwise, tweets are printed to terminal for testing purposes.
armed = False

#============ Do not modify below this line ============#

script_path = os.path.dirname(os.path.realpath(sys.argv[0]))
catalog_file = os.path.join(reposado_root, 'metadata','ProductInfo.plist')
cached_file = str(script_path) + '/ProductInfoCached.plist'
updated = False

auth = tweepy.OAuthHandler(ckey, csecret)
auth.secure = True
auth.set_access_token(atok, asecret)
api = tweepy.API(auth)


def updateCached():
    # copies live catalog to local cached file
    shutil.copy(catalog_file, cached_file)


def checkHashes():
    # compares sha256 hash of cached & live file to detect changes.
    # Returns True if files are different.
    hashed_origin = hashlib.sha256()
    hashed_cached = hashlib.sha256()

    with open(catalog_file, 'rb') as ofile:
        buf = ofile.read()
        hashed_origin.update(buf)

    with open(cached_file, 'rb') as cfile:
        cbuf = cfile.read()
        hashed_cached.update(cbuf)

    if ((hashed_origin.hexdigest()) == (hashed_cached.hexdigest())):
        return(False)
    else:
        return(True)


def compareCatalogs():
    # Walk through cached & current catalogs.
    # Items missing from cached are assumed to be new.
    current = plistlib.readPlist(catalog_file)
    cached = plistlib.readPlist(cached_file)
    newUpdates = []

    for item in current:
        if not cached.get(item):
            newUpdates.append(item)

    return (newUpdates)


def buildTweets(updates):
    # Walk through new item list, pull details and format the tweets.
    buildList = []
    current = plistlib.readPlist(catalog_file)

    for update in updates:
        buildList.append(''.join([datetime.date.today().strftime("%m/%d/%y"), \
        " ", "New Apple Update ", update, ": ", \
        current.get(update).get('title'), ", version ", \
        current.get(update).get('version')]))

    return(buildList)


def sendTweets(tweetList, armed):
    # Tweets each line if armed, otherwise prints to stdout.
    for tweet in tweetList:
        if armed:
            api.update_status(tweet)
        else:
            print tweet


# Test if the cache file exists - copy current origin if it does not.
if not os.path.isfile(cached_file):
    updateCached()

updated = checkHashes()

if (updated):

    updateList = compareCatalogs()
    tweetList = buildTweets(updateList)
    sendTweets(tweetList, armed)
    updateCached()
