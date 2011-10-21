
"""
Reddit API parser.

Handles major events when interacting with the reddit.com api.

Non-primitive objects returned are normally JSON objects.
by Derv Merkler @ github.com/derv82/reddiwrap

"""

import Web

try:
    import json
except ImportError:
    import simplejson as json


class ReddiWrap:
    """
        Class for interacting with reddit.com
        
        Uses reddit's API. 
        
        Results are commonly returned as JSON objects.
    """
    
    def __init__(self, user='', password=''):
        """
            Initializes instance fields.
            
            Logs into reddit if user and password are given.
        """
        
        # object we will use to communicate with the WWW
        self.web = Web.Web(user_agent='ReddiWrap') 
        
        self.modhash = ''
        
        self.before   = None
        self.after    = None
        self.last_url = ''
        
        # Sets instance fields, logs in user if able.
        self.switch_user(user, password)
    
    
    
    ####################
    # LOGGING IN & OUT #
    ####################
    
    def switch_user(self, user, password):
        """
            Logs into 'user' using 'password' if given.
            "Logs out" of account if user and password are both ''
            
            This method will clear all cookies.
            During logout, this method will reset 'modhash'.
        """
        self.user     = user
        self.password = password
        
        self.logged_in = False
        
        if user != '' and password != '':
            # Try to login
            self.logged_in = self.login()
        
        else:
            # "Log out" by clearing cookies
            self.modhash = ''
            self.web.clear_cookies()
    
    
    def login(self, user='', password=''):
        """
            Logs into reddit. 
            The auth cookie is stored in the cookiejar (cj) in the 'self.web' object.
            
            More info on this process can be found here:
                
                https://github.com/reddit/reddit/wiki/API%3A-login
        """
        
        if user != '' and password != '': 
            self.user     = user
            self.password = password
        
        # Clear any cookies we may have accumulated.
        self.web.clear_cookies()
        
        # Reset the modhash
        self.modhash = ''
        
        # login dict
        dict = {}
        dict['user']     = self.user
        dict['passwd']   = self.password
        dict['api_type'] = 'json'
        
        r = self.web.post('http://www.reddit.com/api/login/%s' % self.user, dict)
        
        if r.find("WRONG_PASSWORD") != -1:
            # invalid password
            return False
        
        elif r.find('RATELIMIT') != -1:
            # rate limit reached.
            print 'rate limit reached, wait before logging in again.'
            return False
            
        elif r.find('redirect'):
            # correct password
            
            # set the modhash.
            js = json.loads(r)
            if js['json'].get('data') == None: return False
            self.modhash = js['json']['data']['modhash']
            
            return True
        
        # some other unexpected response
        return False
    
    
    def logout(self):
        """
            Very simple logout method. 
            Clears cookies, resets modhash.
        """
        self.switch_user('', '')
        
    
    ################
    # WEB REQUESTS #
    ################
    
    @staticmethod
    def fix_url(url):
        """
            'Corrects' a given URL as needed. Used by self.get()
            
            Ensures:
                * url begins with http://
                * reddit.com is used instead of www.reddit.com
                * urls that are relative (start with '/') use reddit.com
        """
        result = url
        
        if result.startswith('/'):
            result = 'http://reddit.com' + result
        
        if not result.startswith('http://'):
            result = 'http://' + result
        
        # Get does not like 'www.' for some reason.
        result = result.replace('www.reddit.com', 'reddit.com')
        
        if result.find('.json') == -1:
            
            q = result.find('?')
            if q == -1:
                result += '.json'
            else:
                result = result[:q] + '.json' + result[q:]
            
        return result
    
    
    def get(self, url):
        """
            Returns a json object containing data from the URL.
            Returns None if unable to get data from URL.
            
            'url' must be within the reddit.com domain!
            Note that relative addressing is allowed, eg .get('/r/pics')
            
            This method automatically adds the appropriate '.json' 
            extension to the URL if not already included.
            
            This methods automatically updates self.modhash!
            In this way, we handle modhash within this class; which means 
            users of this class don't have to worry about modhash.
            
            Examples:
                * reddit.get('http://reddit.com/user/karmanaut/submitted')
                * reddit.get('/r/all/new.json')
                * reddit.get('http://reddit.com/search?q=funny?sort=new')
                
        """
        
        url = self.fix_url(url)
        
        self.last_url = url
        
        r = self.web.get(url) # Get the JSON response via reddit's API
        
        if r == '' or r == '""': return None # Server gave null response.
        
        try:
            js = json.loads(r)
        except ValueError: return None # If it's not JSON, we can't parse it.
        
        # If the response contains a list of data objects...
        if isinstance(js, list):
            data = js[0]['data']
        
        # or simply the data object...
        else:
            data = js.get('data')
        
        if data == None: return None             # We must have a 'data' object.
        
        # Set the variables to keep track of the user hash and current page.
        self.modhash = data.get('modhash')
        self.before  = data.get('before')
        self.after   = data.get('after')
        
        # Return the children if there are any. 
        # This saves an extra step in the process of iterating over posts/comments.
        if data.get('children') != None:
            return data['children']
        
        return js
     
    
    
    ##########
    # VOTING #
    ##########
    
    def vote(self, id, direction):
        """
            Votes for a post or comment.
            
            Returns false if 'user_required' error is received, True otherwise.
            
            id                - ID of the post/comment.
                                    Preceeded by "t3_" for post or "t1_" for comment.
            
            direction - 1 to upvote, -1 to downvote, 0 to rescind vote.
        """
        
        dict = {}
        dict['id']  = id
        dict['dir'] = int(direction)
        dict['uh']  = self.modhash
        
        response = self.web.post('http://www.reddit.com/api/vote', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        # Reddit should respond with '{}' if vote was successful.
        return (response == '{}')
    
    
    
    ##############
    # COMMENTING #
    ##############
    
    def get_comments(self, id, sort=''):
        """
            Returns a json object containing the comments of a post.
            Returns None if unable to retrieve.
            
            id     - The ID of the post to retrieve comments of.
            sort - The order to display the comments
                         e.g. 'best', 'hot', 'new', 'controversial', 'top', 'old'
        """
        
        # Remove the t#_ tag
        if id[0] == 't' and id[2] == '_':
            id = id[3:]
        
        url = self.fix_url('http://reddit.com/comments/' + id)
        
        if sort != '':
            url += '?sort=' + sort
        
        self.last_url = url
        
        r = self.web.get(url)
        if r == '': return None
        
        js = json.loads(r)
        
        # response either contains a list (in which case we select the first)
        if isinstance(js, list):
            data   = js[0]['data']
            result = js[1]['data']['children']
        # or simply the data, in which case we grab it.
        else:
            data   = js['data']
            result = js['data']['children']
        
        self.modhash = data.get('modhash')
        self.before  = data.get('before')
        self.after   = data.get('after')
        
        return result
    
    
    def get_user_comments(self, user, sort=''):
        """
            Returns a json object containing the comments of a post.
            Returns None if unable to retrieve.
        """
        url = self.fix_url('http://reddit.com/user/' + user + '/comments')
        if sort != '':
            url += '?sort=' + sort
        
        self.last_url = url
        
        r = self.web.get(url)
        if r == '': return None
        
        js = json.loads(r)
        
        # response either contains a list (in which case we select the first)
        if isinstance(js, list):
            data   = js[0]['data']
            result = js[1]['data']['children']
        # or simply the data, in which case we grab it.
        else:
            data   = js['data']
            result = js['data']['children']
        
        self.modhash = data.get('modhash')
        self.before  = data.get('before')
        self.after   = data.get('after')
        
        return result
    
    
    def comment(self, id, text):
        """
            Comments on either a post or a parent comment,
            depending on what type the 'id' is.
        """
        
        if id.startswith('t3_'):
            # Commenting on a post
            return self.comment_on_post(id, text)
            
        elif id.startswith('t1_'):
            # Commenting on a comment in a post.
            return self.comment_on_comment(id, text)
            
        else: return False
    
    def comment_on_post(self, post_id, text):
        """
            Submits a comment on a post. 
            To comment on a comment, use comment_on_comment.
            
            Returns False if the error 'user_required' is received, True otherwise.
            
            post_id - "t3_" + a 5 character hex string of the post. 
                                ex: t3_hzko5
            
            test        - The comment body to submit.
            
        """
        dict = {}
        dict['uh']      = self.modhash
        dict['thing_id'] = post_id
        dict['text']     = text
        
        response = self.web.post('http://www.reddit.com/api/comment', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return True
    
    
    def comment_on_comment(self, parent_id, text):
        """
            Submits a comment on a another user's comment. 
            To comment on a comment, use comment_on_comment.
            
            Returns False if the error 'user_required' is received, True otherwise.
            
            parent_id - "t1_" + hex string of the parent comment id.
                                ex: t1_c1znqz2
            
            test        - The comment body to submit.
        """
        dict = {}
        dict['uh']     = self.modhash
        dict['parent'] = parent_id
        dict['text']   = text
        
        response = self.web.post('http://www.reddit.com/api/comment', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return True
    
    
    
    ################
    # USER METHODS #
    ################
    
    def user_info(self):
        """
            Returns JSON object containing information about logged-in user.
            
            Returns None if unable to retrieve user info.
            
            More info about what is returned can be found here:
            
                https://github.com/reddit/reddit/wiki/API%3A-me.json
            
            Example:
                info = reddit.user_info()
                print 'user name:', info['name']
                print 'link karma:', info['link_karma']
                print 'comment karma:', info['comment_karma']
                if info['has_mail']:
                    print 'youve got mail!'
        """
        
        js = self.get('http://www.reddit.com/api/me.json')
        if js == None: return None
        
        return js.get('data')
    
    
    def get_subreddits(self):
        """
            Returns list of JSON objects. Each item in the list contains 
            information about the subreddits the user has subscribed to.
            
            Returns empty list [] if unable to retrieve user's subreddits.
            More info about what is returned can be found here:
            
                https://github.com/reddit/reddit/wiki/API%3A-mine.json
        """
        
        js = self.get('http://www.reddit.com/reddits/mine.json')
        
        if js == None or js.get('data') == None: return []
        
        self.modhash = js['data']['modhash']
        
        return js['data']['children']
    
    
    
    ##########
    # SAVING #
    ##########
    
    def save(self, id):
        dict = {}
        dict['id'] = id
        dict['uh'] = self.modhash
        
        response = self.web.post('http://www.reddit.com/api/save', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return (response == '{}')
    
    
    def unsave(self, id):
        dict = {}
        dict['id'] = id
        dict['uh'] = self.modhash
        
        response = self.web.post('http://www.reddit.com/api/unsave', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return (response == '{}')
    
    
    
    ##########
    # HIDING #
    ##########
    
    def hide(self, id):
        dict = {}
        dict['id'] = id
        dict['uh'] = self.modhash
        
        response = self.web.post('http://www.reddit.com/api/hide', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return (response == '{}')
    
    
    def unhide(self, id):
        dict = {}
        dict['id'] = id
        dict['uh'] = self.modhash
        
        response = self.web.post('http://www.reddit.com/api/unhide', dict)
        if response.find('".error.USER_REQUIRED"') != -1:
            return False
        
        return (response == '{}')
    
    
    
    #############
    # SEARCHING #
    #############
    
    def search(self, query, subreddit='', sort=''):
        """
            Searches reddit, returns list of results.
            
            query         - The text to search for.
            
            subreddit - The subreddit to search within.
            
            sort            - Order to sort the results.
                                    valid sorting types: 'new', 'top', 'relevance'
            
            Examples:
                results = reddit.search('girlfriend')
                results = reddit.search('skateboard', subreddit='pics')
                results = reddit.search('birthday', subreddit='pics', sort='new')
            
            After calling search(), you can call get_next() and get_previous()
            to navigate through the pages of search results.
        """
        
        url = '/search?q=' + query
        
        if sort != '':
            url += '&sort=' + sort
        
        if subreddit != '':
            url = '/r/' + subreddit + url + '&restrict_sr=on'
        
        return self.get(url)
    
    
    
    ##############
    # NAVIGATING #
    ##############
    
    """
        Notice that inside of the 'get()' method, we store:
            * the last URL retrieved (self.last_url)
            * the 'before' tag which links to the previous page (self.before)
            * and the 'after' tag which links to the next page (self.after)
            
        Because of this, we can load the 'next' or 'previous' pages of some results.
        
        This will only go to the 'next' or 'previous' page 
            of the LAST PAGE RETRIEVED using get()
        
        This get_next() and get_previous() methods work with:
            * subreddits, 
            * the main page, 
            * search results, 
            * user pages, 
            * possibly others
    """
    def get_previous(self):
        """
            This method returns the same format of information as get(), 
            but for the 'previous' page on reddit.
            
            Returns None if unable to load the previous page.
        """
        
        if self.before == None:
            # No 'previous' link to use.
            # print 'self.before = None (no "previous" page!)'
            return None
            
        url = self.last_url
        
        # Strip out after/before params from the previous URL.
        i = url.find('&after')
        if i != -1: url = url[:i]
        i = url.find('&before')
        if i != -1: url = url[:i]
        i = url.find('?after')
        if i != -1: url = url[:i]
        i = url.find('?before')
        if i != -1: url = url[:i]
        
        if url.find('?') > -1:
            url += '&before=' + self.before
        else:
            url += '?before=' + self.before
        
        url += '&count=25'
        
        return self.get(url)
    
    
    def get_next(self):
        """
            This method returns the same format of information as get(), 
            but for the 'next' page on reddit.
            
            Returns None if unable to load the next page.
        """
        
        if self.after == None:
            # No 'next' link to use.
            # print 'self.after = None (no "next" page!)'
            return None
            
        url = self.last_url
        
        # Strip out after/before params from the previous URL.
        i = url.find('&after')
        if i != -1: url = url[:i]
            
        i = url.find('&before')
        if i != -1: url = url[:i]
        
        i = url.find('?after')
        if i != -1: url = url[:i]
            
        i = url.find('?before')
        if i != -1: url = url[:i]
        
        if url.find('?') > -1:
            url += '&after=' + self.after
        else:
            url += '?after=' + self.after
        
        url += '&count=25'
        
        return self.get(url)
    
    
    def has_previous(self):
        """
            Returns True if there is a 'previous' page, False otherwise.
        """
        return (self.before != None)
    
    
    def has_next(self):
        """
            Returns True if there is a 'previous' page, False otherwise.
        """
        return (self.after != None)
    
    
    
    ###########
    # POSTING #
    ###########
    
    def post_link(self, title, link, subreddit):
        """
            Submits a new link to reddit.
            
            Parameters are self-explanatory.
            
            subreddit - just the name of the subreddit; 'funny', NOT '/r/funny'
            
        """
        
        dict = {}
        dict['uh']    = self.modhash
        dict['kind']  = 'link'
        dict['url']   = link
        dict['sr']    = subreddit
        dict['title'] = title
        dict['r']     = subreddit
        
        dict['renderstyle'] = 'html'
        
        response = self.web.post('http://www.reddit.com/api/submit', dict)
        
        if response.find("You haven't verified your email address") != -1:
            return ''
        
        
        if response.find('already_submitted=true') != -1:
            jres = json.loads(response)
            existing_link = jres['jquery'][12][3][0]
            print 'link already exists:', existing_link
            return ''
        
        link = self.web.between(response, 'call", ["http://www.reddit.com/', '"]')[0]
        
        return link
    
    
    def post_self(self, title, text, subreddit):
        """
            Submits a new "self-post" (text-based post) reddit.
            
            Parameters are self-explanatory.
            
            subreddit - just the name of the subreddit; 'funny', NOT '/r/funny'
        """
        
        dict = {}
        dict['uh']       = self.modhash
        dict['title']    = title
        dict['kind']     = 'self'
        dict['thing_id'] = ''
        dict['text']     = text
        dict['sr']       = subreddit
        dict['id']       = '#newlink'
        dict['r']        = subreddit
        
        dict['renderstyle'] = 'html'
        
        response = self.web.post('http://www.reddit.com/api/submit', dict)
        
        if response.find("You haven't verified your email address") != -1:
            return ''
        
        link = self.web.between(response, 'call", ["http://www.reddit.com/', '"]')[0]
        
        return link
    
    