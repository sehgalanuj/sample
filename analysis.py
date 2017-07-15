#!/usr/bin/env python
#
# Ricardo de O. Schmidt
# July 14, 2017
#
# Description:
#   Receives a string entered by the user in landing.py
#   Sends the string to Google's natural language API for processing
#   Print a message depending on the score of the sentiment analysis on that string
#

import requests
import json
import cgi

def smart_truncate(content, length=100, suffix='...'):
  if len(content) <= length:
    return content
  else:
    return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

# Get the content user typed in the form in landing.py
form = cgi.FieldStorage()
thought = form.getfirst('thought', 'empty')
thought = cgi.escape(thought) # not needed in this case, but helps preventing injection

### SENTIMENT ANALYSIS ###

# URL to access the Google's natural language API, specifically sentiment analysis
# Using API key access
url = 'https://language.googleapis.com/v1/documents:analyzeSentiment?key=AIzaSyAHphLut5sU7BYpTkQUv55AReS5JABtw0I'

# JSON formatted request for sentiment analsyis
json_req = '{"document":{"type":"PLAIN_TEXT","language":"EN","content":"' + thought + '"},"encodingType":"UTF8"}'

# Send the request and store response in rep
rep = requests.post(url, json_req)

# Loads response into JSON format
json_rep = json.loads(rep.text)

# Find the results on score and magnitute of the sentiment analysis
score = json_rep['documentSentiment']['score']
magnitude = json_rep['documentSentiment']['magnitude']

# Depending on score, choose the answer to be presented to the user
if score == 0: # neutral
  message = 'You are quite bland on your statement. Come on, show some emotion!'
elif score > 0.5: # super positive
  message = 'Wow! Someone is having a great day today!'
elif score > 0: # positive
  message = 'You seem to be following a positive vibe today!'
elif score < -0.5: # super negative
  message = 'Wow! Where do you keep all that anger?'
elif score < 0: # negative
  message = 'Come on, being more positive can help improving your day!'

# Output to be printed about the sentiment analysis
html_return = "Content-Type: application/json\n"
json_return = {'response': message, 'entities': []}

### ENTITIES ANALYSIS ###

# URL to access the entities analysis, using the same API key
url = 'https://language.googleapis.com/v1/documents:analyzeEntities?key=AIzaSyAHphLut5sU7BYpTkQUv55AReS5JABtw0I'

# JSON formatted request for entities analysis
json_req = '{"encodingType":"UTF8","document":{"type":"PLAIN_TEXT","content":"' + thought + '"}}'

# Send the request and store response in rep
rep = requests.post(url, json_req)

# Loads response into JSON format
json_rep = json.loads(rep.text)

# Get Wikipedia references that were returned, if any
# and create a list of them as reading suggestion along with a text snippet, thumbnail and 
for ent in json_rep['entities']:
  if 'wikipedia_url' in ent['metadata']:
    subject = ent['metadata']['wikipedia_url'].replace('http://en.wikipedia.org/wiki/', '')
    wikiAPI = 'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages%7Cextracts&redirects=1&formatversion=2&piprop=thumbnail&pithumbsize=150&pilimit=1&exintro=1&explaintext=1&titles=' + subject
    rep = requests.get(wikiAPI)
    json_rep = json.loads(rep.text)
    
    if 'thumbnail' in rep.text:
      imgURL = json_rep['query']['pages'][0]['thumbnail']['source']
    else:
      imgURL = 'http://www.pbgnetworks.com/Style%20Library/PBGDesignModule/Images/no_image_found.jpg'

    if 'extract' in rep.text:
      wikiSnippet = smart_truncate(json_rep['query']['pages'][0]['extract'], length=1200)
    else:
      wikiSnippet = "Sorry, no information was found..."

    json_return['entities'].append({'name': ent['name'], 
                                    'details': wikiSnippet,
                                    'img': imgURL,
                                    'url': ent['metadata']['wikipedia_url']})

html_return = "Content-Type: application/json\n\n" + json.dumps(json_return)

# Finally, print the message
print html_return
