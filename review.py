import re

class Review:
  review_number = 1
  def __nonzero__(self):
    return bool(self.reviewers > 0 or self.revisions > 1)

  # __bool__ function in case we ever upgrade to Python 3.x  
  def __bool__(self):
    return self.__nonzero__()

  def __init__(self, commit, repo):
    self.repo = repo

    message = commit['message']
    self.reviewers = set(self.__get_reviewers(message))
    self.revisions = self.__get_revisions(message)
    self.revisions.append(commit['id'])
    self.joined_review_id = -1

  def __get_reviewers(self, message):
    match = re.search(r"reviewers?\s*\((.*?)\)", message.lower())
    return map(str.strip, map(str, match.expand(r"\1").split(','))) if match else []
    
  def __get_revisions(self, message):
    match = re.search(r"rev(?:ision)?s?\s*\(\s*((?:(?:[0-9a-f]{8,})\s*,\s*)*(?:[0-9a-f]{8,}))\s*\)", message.lower())
    return map(str.strip, map(str, match.expand(r"\1").split(','))) if match else []
    
  def set_review_id(self, review_id, commit_list):
    if self.joined_review_id == review_id:
      return
  
    self.joined_review_id = review_id
    for commit_hash in self.revisions:
      commit_list[commit_hash].set_review_id(review_id, commit_list)

