reddiwrap
---------

reddiwrap is a python wrapper for communicating with the reddit.com API.

----

Interacting with the reddit API is not very difficult, but figuring it out can take a while.

This class allows the interaction with reddit to be simple and easy.

reddiwrap makes it easy to:

  * login,
  * view user info,
  * vote on posts and comments,
  * save/unsave posts,
  * submit links and self-posts,
  * search reddit for posts,
  * comment on posts and other comments,
  * load posts from:
    * subreddits,
    * user pages,
    * and search results.
  * navigate to 'next' and 'previous' pages.
  

Sample usage:
-------------

    # To upvote the first post on the /r/pics front page.
    
    from ReddiWrap import ReddiWrap
    
    # Creates class, logs into account 'user' with the password 'pass' .
    reddit = ReddiWrap('user', 'pass') 
    
    if not reddit.logged_in:      # Ensure we logged in correctly
      print 'unable to log in.'
      exit(1)
    
    pics = reddit.get('/r/pics')  # Get posts on the front page of reddit.com/r/pics
    
    for post in pics:             # Iterate over each post
      
      id = post['data']['name']   # Get the current post's ID (5-char string)
      
      reddit.vote(id, 1)          # Upvote this post. A -1 would mean downvote, 0 rescinds the vote.
      
      break                       # Stop after the first post


More examples showing how reddiwrap works is available in [ReddiWrapTest.py](https://github.com/derv82/reddiwrap/blob/master/ReddiWrapTest.py).

