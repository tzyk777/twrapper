class User(object):
    def __init__(self, name, time_zone, created, lang, location, tweets, following, followers):
        self.name = name
        self.time_zone = time_zone
        self.created = created
        self.lang = lang
        self.location = location
        self.tweets = tweets
        self.following = following
        self.followers = followers


class Tweet(object):
    def __init__(self, user, created, text, lang, topic):
        self.user = user
        self.created = created
        self.text = text
        self.lang = lang
        self.topic = topic
