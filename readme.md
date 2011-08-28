reddiwrap
---------

reddiwrap is a python wrapper for communicating with the reddit.com API.

----

Interacting with the reddit API is simple, but figuring it out can take a while.

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
  
----

Sample usage:
-------------

    # To upvote the first post on the /r/pics front page.
    
    from ReddiWrap import ReddiWrap
    
    # Login
    reddit = ReddiWrap('user_name_here', 'password_here')
    
    # Ensure we logged in correctly
    if not reddit.logged_in:
      print 'not logged in. invalid pw?'
      exit(1)
    
    # get every post from reddit.com/r/pics
    pics = reddit.get('/r/pics')
    
    # Iterate over each post
    for post in pics['data']['children']:
      
      # Get this post's ID
      id = post['data']['name']
      
      # Upvote this post
      reddit.vote(id, 1)
      
      # Stop after the first post
      break


