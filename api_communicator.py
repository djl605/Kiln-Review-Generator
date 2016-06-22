import os
import re
import json
import urllib2
from review import Review
from urllib import urlencode
from utils import eprint

def api(subdomain, url):
  return 'http://' + subdomain + '.kilnhg.com/API/2.0/' + url


def slurp(url, token, params={}, post=False, raw=False):
  params['token'] = token
  params = urlencode(params, doseq=True)
  handle = urllib2.urlopen(url, params) if post else urllib2.urlopen(url + '?' + params)
  content = handle.read()
  obj = content if raw else json.loads(content)
  handle.close()
  return obj
  
def test_token(url, token):
  reply = slurp(api(url, 'Person'), token, post=False)
  return not (u'errors' in reply)

def create_review(review, subdomain, token, users):
  repo = review.repo
  
  reviewers = []
  for reviewer in review.reviewers:
    for user in users:
      if reviewer == user['username']:
        reviewers.append(user['ixUser'])
        break
    else:
      eprint('ERROR: Attempting to assign reviewer to unrecognized name: ' + reviewer)
  
  revisions = []
  for revision in review.revisions:
    if revision:
      revisions.append(revision)
    
  return slurp(api(subdomain, 'Review/Create'), token, params=dict(ixRepo=repo, ixReviewers=reviewers, revs=revisions), post=False)
  

# Function: process_hook
# Handles incoming Kiln webhooks by parsing them and creating necessary reviews
def process_hook(payload, subdomain, users, token):
  commit_list = {}

  for commit in payload['commits']:
    review = Review(commit, payload['repository']['id'])
    commit_list[commit['id']] = review
    
  reviews_to_create = join_reviews(commit_list)
  for r in reviews_to_create.values():
    if r.reviewers:
      reply = create_review(r, subdomain, token, users)
      eprint(reply)
  

def join_reviews(commit_list):
  expand_revisions(commit_list)
  make_revision_links_two_ways(commit_list)
  create_review_ids(commit_list)
  return generate_linked_review_list(commit_list.values())

def expand_revisions(commit_list):
  for commit_hash in commit_list.keys():
    expand_review_revisions(commit_list[commit_hash], commit_list.keys())

def expand_review_revisions(review, commit_list):
  review.revisions = set([expand_revision(r, commit_list) for r in review.revisions])
  
# Function: expand_revision
def expand_revision(revision, commit_list):
  full_hash = [commit for commit in commit_list if revision in commit]
  if len(full_hash) == 0:
    eprint('Tried to attach review to commit that is not in this push')
    return None
  elif len(full_hash) != 1:
    eprint('Revision matches more than one hash in this push: Not adding any to the review')
    return None
  else:
     return full_hash[0]


def make_revision_links_two_ways(commit_list):
  for commit_hash in commit_list.keys():
    review_object = commit_list[commit_hash]
    for linked_revision in review_object.revisions:
      commit_list[linked_revision].revisions.add(commit_hash)
      
def create_review_ids(commit_list):
  next_review_id = 1
  for commit_hash in commit_list.keys():
    commit_list[commit_hash].set_review_id(next_review_id, commit_list)
    next_review_id += 1

def generate_linked_review_list(unlinked_reviews):
  reviews = {}
  for unlinked_review in unlinked_reviews:
    review_id = unlinked_review.joined_review_id
    if review_id in reviews:
      full_review = reviews[review_id]
      full_review.reviewers |= unlinked_review.reviewers
      full_review.revisions |= unlinked_review.revisions
    else:
      reviews[review_id] = unlinked_review
  
  return reviews
  