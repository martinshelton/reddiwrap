RedditWrap
----------

RedditWrap is a python wrapper for communicating with the reddit.com API.

----

Interacting with the reddit API is simple, but figuring it out can take a while.

This class allows the interaction with reddit to be simple and easy.

RedditWrap makes it easy to:

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

    # To upvote every post on the /r/pics front page.
    
    from RedditWrap import RedditWrap
    
    reddit = RedditWrap('sample_username', 'password')
    
    # get every post from reddit.com/r/pics
    pics = reddit.get('/r/pics')
    
    # Iterate over each post
    for post in pics['data']['children']:
      
      # Get the post ID
      id = post['data']['name']
      
      # Upvote each post
      reddit.vote(id, 1)

