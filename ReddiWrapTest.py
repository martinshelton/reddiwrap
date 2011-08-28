#!/usr/bin/env python

"""

  Class for showing how to use the reddit python wrapper (ReddiWrap.py)
  
"""

from ReddiWrap import ReddiWrap
import json


print 'logging in',

#   LOGIN
reddit = ReddiWrap('username_her', 'password_here')

print reddit.logged_in

if not reddit.logged_in:
  print 'unable to log in.'
  exit(0)


#   LOGOUT
"""
reddit.logout()
"""

#   GET USER INFO

info = reddit.user_info()
print 'user name:', info['name']
print 'link karma:', info['link_karma']
print 'comment karma:', info['comment_karma']
if info['has_mail']:
  print 'you\'ve got mail!'


#   SUBMIT A LINK
# print 'submitting a link', reddit.post_link('This website is awesome!', 'http://www.imgur.com', 'pics')

#   SUBMIT A SELF-POST
#print 'submitting a self-post', reddit.post_self('Why come you no have tattoo?', 'Inquiring minds want to know.', 'AskReddit')

#   GET/ITERATE OVER USER'S SUBREDDITS
"""
for subreddit in reddit.get_subreddits():
  data = subreddit['data']
  print 'subscribed subreddit:', data['url']
"""


#   GET POSTS IN SUBREDDIT
js = reddit.get('/r/pics')

#   GET POSTS BY USER
#js = reddit.get('/user/karmanaut/submitted')

#   GET POSTS IN SEARCH RESULTS
#js = reddit.search('patton', sort='top', subreddit='reddit.com')


#   ITERATE OVER POSTS
for post in js['data']['children']:
  
  # post_data contains information about this post
  post_data = post['data']
  
  if post_data.get('title') == None: continue
  
  # For example, the title of the current post:
  print 'first post title:', post_data['title']
  
  # In order to interact with the post (vote, view comments, etc),
  # we need the post's "ID"
  id = post_data['name']
  break

  
#   LOAD 'NEXT' PAGE OF POSTS
if reddit.has_next():
  js = reddit.get_next()
  for post in js['data']['children']:
    post_data = post['data']
    
    if post_data.get('title') == None: continue
    
    print 'first post title:', post_data['title']
    break


#   LOAD 'PREVIOUS' PAGE OF POSTS
if reddit.has_previous():
  js = reddit.get_previous()
  for post in js['data']['children']:
    post_data = post['data']
    
    if post_data.get('title') == None: continue
    
    print 'first post title:', post_data['title']
    break



#   VOTE
"""
print 'voting on', id
print 'vote', reddit.vote(id, 1) # 1 to upvote, -1 to downvote, 0 to remove vote, 
"""

#   SAVE
"""
print 'saving', id
print 'saved', reddit.save(id)
"""

#   UNSAVE
"""
print 'unsaving', id
print 'unsaved', reddit.unsave(id)
"""

#   COMMENT ON POST
"""
print 'commenting on', id
print 'comment', reddit.comment(id, 'squibbily flappity too')
"""

#   ITERATE OVER COMMENTS OF POST
"""
post = reddit.get_comments(id)  # get the comments

for comment in post['children']:
  comment_data = coment['data']
  comment_id = comment_data['name']
  break
"""

#   COMMENT ON COMMENT
"""
print 'commenting on comment:', comment_id
print 'result', reddit.comment(comm_id, 'herp derp?')
"""


