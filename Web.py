
"""

Web class.

Holds commonly-used HTTP/web request/post methods.

by Derv Merkler @ github.com/derv82
"""

import time

import urllib2, cookielib
from urllib import urlencode
from httplib import HTTPException

class Web:
  """
    Class used for communicating with web servers.
  """
  
  def __init__(self, user_agent=None):
    """
      Sets this class's user agent.
    """
    self.urlopen = urllib2.urlopen
    self.Request = urllib2.Request
    self.cj      = cookielib.LWPCookieJar()
    self.opener  = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
    urllib2.install_opener(self.opener)
    
    if user_agent != None:
      self.user_agent = user_agent
    else:
      self.user_agent = 'ReddiWrap'
  
  
  def get(self, url):
    """
      Attempts GET request with web server.
      
      Returns html source of a webpage (string).
      Returns '' if unable to retrieve webpage for any reason.
      
      Will attempt to repeatedly post if '504' response error is received
      or 'getaddrinfo' fails.
    """
    headers = {'User-agent' : self.user_agent}
    
    try_again = True
    while try_again:
      try:
        req = self.Request(url, '', headers)
        handle = self.urlopen(req)
        
      except IOError, e:
        if str(e) == 'HTTP Error 504: Gateway Time-out' or \
           str(e) == 'getaddrinfo failed':
          try_again = True
          time.sleep(2)
        
        else: return ''
      
      except HTTPException: return ''
      except UnicodeEncodeError: return ''
        
      else:
        try_again = False
      
    result = handle.read()
    
    return result
  
  
  def post(self, url, postdict=None):
    """
      Attempts POST request with web server.
      
      Returns response of a POST request to a web server.
      'postdict' must be a dictionary of keys/values to post to the server.
      Returns '' if unable to post/retrieve response.
      
      Will attempt to repeatedly post if '504' response error is received
      or 'getaddrinfo' fails.
    """
    headers = {'User-agent' : self.user_agent}
    
    data = ''
    if postdict != None:
      data = urlencode(postdict)
    
    try_again = True
    while try_again:
      try:
        req = self.Request(url, data, headers)
        handle = self.urlopen(req)
        
      except IOError, e:
        if str(e) == 'HTTP Error 504: Gateway Time-out' or \
           str(e) == 'getaddrinfo failed':
          try_again = True
          time.sleep(2)
        
        else: return ''
      
      except HTTPException: return ''
      except UnicodeEncodeError: return ''
        
      else:
        try_again = False
      
    result = handle.read()
    
    return result
  
  
  def download(self, url, save_as):
    """
      Downloads a file from 'url' and saves the file locally as 'save_as'.
      Returns True if download is successful, False otherwise.
    """
    
    result = False
    output = open(save_as, "wb")
    
    try:
      image_on_web = urlopen(url)
      while True:
        buf = image_on_web.read(65536)
        if len(buf) == 0:
          break
        output.write(buf)
      result = True
      
    except IOError, e: pass
    except HTTPException, e: pass
    
    ouput.close()
    return result
  
  
  def clear_cookies(self):
    """
      Clears cookies in cookie jar.
    """
    self.cj.clear()
  
  
  def set_user_agent(user_agent):
    """
      Changes the user-agent used when connecting.
    """
    self.user_agent = user_agent
  
  
  def between(self, source, start, finish):
    """
      Helper method. Useful when parsing responses from web servers.
      
      Looks through a given source string for all items between two other strings, 
      returns the list of items (or empty list if none are found).
      
      Example:
        test = 'hello >30< test >20< asdf >>10<< sadf>'
        print between(test, '>', '<')
        
      would print the list:
        ['30', '20', '>10']
    """
    result = []
    i = source.find(start)
    j = source.find(finish, i + len(start) + 1)
    
    while i >= 0 and j >= 0:
      i = i + len(start)
      result.append(source[i:j])
      i = source.find(start, i + len(start) + 1)
      j = source.find(finish, i + len(start) + 1)
    
    return result
  
  