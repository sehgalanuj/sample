#!/usr/bin/env python
#
# Ricardo de O. Schmidt
# Juluy 14, 2017
#
# Description:
#   Landing page that receives an input string from user
#   and calls analysis.py to analyze and process the string
#   using Google natural language API
#

with open('index.html','r') as f:
    output = f.read()
    print "Content-type: text/html"
    print
    print output
