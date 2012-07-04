#!/usr/bin/python

from ReddiWrap import ReddiWrap

reddit = ReddiWrap(user_agent='ReddiWrap')

USERNAME = 'your_username'
PASSWORD = 'your_password'

# Testing login
login = reddit.login(user=USERNAME, password=PASSWORD)
if login != 0:
	print 'unable to log in:', login
	print 'remember to change USERNAME and PASSWORD'
	exit(1)
print 'logged in as %s' % reddit.user

uinfo = reddit.user_info()

created = int(uinfo.created)
print 'account created on:', reddit.time_to_date(created)
print 'time since account created:', reddit.time_since(created)

# Retrieve posts in a subreddit
posts = reddit.get('/r/all/top?t=day')
print 'top posts for the day in /r/all:'
for post in posts:
	print '\t',post

# Store first post for other functions
post = posts[0]

# Retrieve comments for the first post
print 'fetching comments for "%s"' % (post.title)
reddit.fetch_comments(post)
for comment in post.comments:
	# Print first 60 chars of all root-level comments
	print '%s: "%s"' % (comment.author, comment.body[:60].replace('\n',' '))

# Store first comment for other functions
comment = post.comments[0]

# Upvote post
reddit.upvote(post)
# Upvote comment
reddit.upvote(comment)
# Save post
reddit.save(post)

# Reply to post
print 'replying to post "%s"' % (post.title)
result = reddit.reply(post, "I can't believe this is in /r/%s" % post.subreddit)
if result == {}:
	print 'unable to reply to post'
else:
	print 'replied to %s, %s' % (result['parent'], result['id'])

# Reply to comment
print 'replying to comment by %s' % (comment.author)
result = reddit.reply(comment, "I like the part where you said:\n\n>%s" % comment.body.replace('\n\n', '\n\n>'))
if result == {}:
	print 'unable to reply to post'
else:
	print 'replied to %s, %s' % (result['parent'], result['id'])



# Testing submitting link
print 'submitting link to /r/freshbreath',
result = reddit.post_link('best website ever', 'http://derv.us', 'freshbreath')
if result == '':
	print 'unable to submit link!'
else:
	print 'done.', result

# Testing submitting self-post
print 'submitting self-post to /r/freshbreath',
result = reddit.post_self('DAE breathe?', 'I thought I was the only one!', 'freshbreath')
if result == '':
	print 'unable to submit link!'
else:
	print 'done.', result


# Testing current user info
uinfo = reddit.user_info()
print 'link karma:    %d' % uinfo.link_karma
print 'comment karma: %d' % uinfo.comment_karma


# Testing modmail
modmsgs = reddit.get('/message/moderator')
for msg in modmsgs:
	print msg
	reddit.mark_message(msg) # mark as read


# Checking spam/report queue
posts = reddit.get('/r/freshbreath/about/reports/')
#posts = reddit.get('/r/freshbreath/about/spam/')
for post in posts:
	print post


# Subscribe to spacedicks!
subs = reddit.get('/reddits')
# 'subs' is reddit's huge list of subreddits
subbed = False
while not subbed:
	# Iterate over all subreddits
	for sub in subs:
		if sub.display_name == 'spacedicks':
			reddit.subscribe(sub)
			print 'subscribed to spacedicks'
			subbed = True
			break
	if not subbed and reddit.has_next():
		print 'loading next page of subreddits...'
		subs = reddit.get_next()
	else:
		break


# Unsub from spacedicks!
subs = reddit.get('/reddits/mine')
# 'subs' is the user's list of subscribed subreddits
for sub in subs:
	if sub.display_name == 'spacedicks':
		reddit.subscribe(sub, unsub=True)
		break


# Test marking NSFW, approving/removing/reporting/distinguishing/spam
# Assumes first post in user's history is in subreddit user is moderator of
posts = reddit.get('/user/%s/submitted' % (reddit.user))
if len(posts) > 0:
	post = posts[0]
	print post
	print 'marking...',  reddit.mark_nsfw(post)
	print 'reporting...',reddit.report(post)
	print 'removing...', reddit.remove(post)
	print 'spamming...', reddit.spam(post)
	print 'approving...',reddit.approve(post)
	print 'distinguishing...',reddit.distinguish(post)


# Test receiving/replying messages
msgs = reddit.get('/message/messages')
for msg in msgs:
	# Print first 40 char of all messages
	print msg.__repr__()[:40]
if len(msgs) > 0:
	msg = msgs[0]
	# Reply to first message
	print 'replying to: %s' % (msg),
	success = reddit.reply(msg, "Sure, I'll s***y_watercolor that in ALL CAPS while trapped in my anus... NAUT!")
	if success == {}:
		print '\nunable to reply!'
	else:
		print '\nreply successful:',success['id']


# Retrieve first 100 subreddits
import time # For sleep(), to avoid API rate limit
count = 0
subs = reddit.get('/reddits')
while True:
	for sub in subs: 
		# Print 10 per line
		print '%s,' % (sub.display_name),
		count += 1
		if count % 10 == 0: print ''
	if count >= 100 or not reddit.has_next(): break
	time.sleep(2) # One request every 2 seconds.
	subs = reddit.get_next()


# Testing get_next and get_prev (moving forward and backward)
posts = reddit.get('/r/askscience')
print len(posts), 'posts in AskScience page #1'
for post in posts: print post
print '\n'

posts = reddit.get_next()
print len(posts), 'posts in AskScience page #2'
for post in posts: print post
print '\n'

posts = reddit.get_previous()
print len(posts), 'posts in AskScience page #1'
for post in posts: print post
print '\n'


# Testing get_next(). Gets the 'next' page 2 times in a row
posts = reddit.get('/r/AskReddit')
for i in xrange(0, 3):
	for post in posts:
		print post
	if not reddit.has_next():
		break
	posts = reddit.get_next()


def iterate_comments(comment, depth=0):
	""" Recursively iterate and 'pretty print' comments. """
	if isinstance(comment, list):
		to_it = comment
	else:
		to_it = comment.children
		print '  ' * depth,
		print comment.__str__()[:80].replace('\n', '\\n')
	for comm in to_it:
		iterate_comments(comm, depth + 1)

# Retrieve and iterate over comments recursively
posts = reddit.get('/r/freshbreath')
for post in posts:
	if post.num_comments == 0: continue
	print post
	reddit.fetch_comments(post)
	print '\ncomments:\n'
	iterate_comments(post.comments)
