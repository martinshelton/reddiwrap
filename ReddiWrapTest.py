#!/usr/bin/env python

"""

  Class for showing how to use the reddit python wrapper (ReddiWrap.py)
  
"""

from ReddiWrap import ReddiWrap

import json

reddit = ReddiWrap()


#   LOGIN
"""
print 'logging in',

reddit = ReddiWrap('username_here', 'password_here')

print reddit.logged_in

if not reddit.logged_in:
  print 'unable to log in.'
  exit(0)
"""


#   LOGOUT
"""
reddit.logout()
"""


#   GET USER INFO
"""
info = reddit.user_info()
if info != None:
  print 'user name:', info['name']
  print 'link karma:', info['link_karma']
  print 'comment karma:', info['comment_karma']
  if info['has_mail']:
    print 'you\'ve got mail!'
"""


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
posts = reddit.get('/r/reddit.com')

#   GET POSTS BY USER
#posts = reddit.get('/user/karmanaut/submitted')

#   GET POSTS IN SEARCH RESULTS
#posts = reddit.search('patton', sort='top', subreddit='reddit.com')


#   ITERATE OVER POSTS
for post in posts:
	
	# post_data contains information about this post
	post_data = post['data']
	
	if post_data.get('title') == None: continue
	
	# For example, the title of the current post:
	print 'first post title, front page = ', post_data['title']
	
	# In order to interact with the post (vote, view comments, etc),
	# we need the post's "ID"
	id = post_data['name']
	break

  
#   LOAD 'NEXT' PAGE OF POSTS

if reddit.has_next():
	for post in reddit.get_next():
		post_data = post['data']

		if post_data.get('title') == None: continue

		print 'first post title, "next" page:', post_data['title']
		break



#   LOAD 'PREVIOUS' PAGE OF POSTS

if reddit.has_previous():
	for post in reddit.get_previous():
		post_data = post['data']

		if post_data.get('title') == None: continue

		print 'first post title, "previous" page:', post_data['title']
		break



#   VOTE
"""
print 'voting on', id
print 'voted?', reddit.vote(id, 0) # 1 to upvote, -1 to downvote, 0 to remove vote, 
"""

#   SAVE
"""
print 'saving', id
print 'saved sucessfully?', reddit.save(id)
"""

#   UNSAVE
"""
print 'unsaving', id
print 'unsaved successfully?', reddit.unsave(id)
"""

#   HIDE
"""
print 'hiding', id
print 'hid successfully?', reddit.hide(id)
"""

#   UNHIDE
"""
print 'unhiding', id
print 'unhid successfully?', reddit.unhide(id)
"""

#   COMMENT ON POST
"""
print 'commenting on', id
print 'comment successful?', reddit.comment(id, 'Mmm... Yes, shallow and pedantic.')
"""

#   ITERATE OVER COMMENTS IN A POST
"""
for comment in reddit.get_comments(id): # get the comments in a post by the post ID
  
  comment_data = comment['data']
  comment_id = comment_data['name']
  break
"""

#   COMMENT ON COMMENT
"""
print 'commenting on comment:', comment_id
print 'comment succesful?', reddit.comment(comment_id, 'Well, I *never*.')
"""


#   ITERATE OVER USER'S COMMENTS

for comment in reddit.get_user_comments('karmanaut', sort='top'): # get the user's comments
  
	comment_data = comment['data']

	# Print the first 30 characters of each of their comments.
	print comment_data['body'][:30].replace('\n', '')
	comment_id = comment_data['name']

	# break

print comment_id