# -*- coding: utf-8 -*-
import re
import twitter_text

class TweetStats(dict):

    # Object properties

    text = ''
    re_non_word = re.compile("\W+")
    re_uri = re.compile("https?://\S+")

    # Override dict functions

    def __init__(self):
        self['stats'] = {}

    def update(self, tweet):
        self.set_text(tweet)
        self.update_word_stats(tweet)
        self.update_entities_stats(tweet)


    # Custom functions

    def set_text(self, tweet):
        """Set text property to normalized text of tweet."""

        text = tweet['text']

        # remove URIs
        text = re.sub(self.re_uri,"", text)
        # lower case string and remove non word characters
        text = re.sub(self.re_non_word, " ",  text.lower()).strip()

        self.text = text


    def get_phrase_list(self, words, length):
        """Get a list of word lists from given list of words of the given length.

        Returns list of lists or None if length of given list is less than given length."""

        if len(words) >= length:
            return [words[i:i+length] for i in range(len(words) - length + 1)]
        else:
            return None


    def update_stats(self, idx, key):
        stats = self['stats']
        if not stats.has_key(idx):
            stats[idx] = {}
        if stats[idx].has_key(key):
            stats[idx][key] += 1
        else:
            stats[idx][key] = 1


    def update_word_stats(self, tweet):

        words = self.text.split()

        # process single words
        for word in words:
            self.update_stats('words', word)

        # process 2 word lists
        pairs = self.get_phrase_list(words, 2)
        if pairs is not None:
            for word_pair in pairs:
                self.update_stats('word_pairs', str(word_pair))

        # process 3 word lists
        triples = self.get_phrase_list(words, 3)
        if triples is not None:
            for word_triple in triples:
                self.update_stats('word_triples', str(word_triple))


    def get_entities(self, text):
        """Extract entities from tweet as text and return an entity dict.

        Function modified from:
        https://github.com/ptwobrussell/Mining-the-Social-Web/blob/master/python_code/the_tweet__extract_tweet_entities.py
        """

        extractor = twitter_text.Extractor(text)

        entities = {}
        entities['user_mentions'] = []
        for um in extractor.extract_mentioned_screen_names_with_indices():
            entities['user_mentions'].append(um)

        entities['hashtags'] = []
        for ht in extractor.extract_hashtags_with_indices():

            # massage field name to match production twitter api
            ht['text'] = ht['hashtag']
            del ht['hashtag']
            entities['hashtags'].append(ht)

        entities['urls'] = []
        for url in extractor.extract_urls_with_indices():
            entities['urls'].append(url)

        return entities


    def update_entities_stats(self, tweet):
        """Process tweet entities and add them to tweet_stats dict."""

        entities = self.get_entities(tweet['text'])
        for ent in entities:
            if entities[ent]:
                e_list = entities[ent]
                for k in e_list:
                    v = None
                    if k.has_key('url'):
                        v = k['url']
                    # FIXME Further normalize text?
                    if k.has_key('text'):
                        v = k['text'].lower()
                    if v:
                        tweet_stats = self['stats']
                        if not tweet_stats.has_key(ent):
                            tweet_stats[ent] = {}
                        if not tweet_stats[ent].has_key(v):
                            tweet_stats[ent][v] = 1
                        else:
                            tweet_stats[ent][v] += 1

if __name__ == "__main__":

    tweet = {u'iso_language_code': u'en', u'to_user_id_str': None, u'text': u'PCMS 4n1 Combo - MSI Wind U100-641US 10-Inch #Netbook Carrying Bag with AC and DC Adapter Charger Home / Car / A... http://amzn.to/f2wssq', u'from_user_id_str': u'104656176', u'profile_image_url': u'http://a2.twimg.com/profile_images/771807838/sleeper-chairs-03-300x146_normal.jpg', u'id': 56183119782477824L, u'source': u'&lt;a href=&quot;http://twitterfeed.com&quot; rel=&quot;nofollow&quot;&gt;twitterfeed&lt;/a&gt;', u'id_str': u'56183119782477824', u'from_user': u'sleeperchairs', u'from_user_id': 104656176, u'to_user_id': None, u'geo': None, u'created_at': u'Fri, 08 Apr 2011 02:34:34 +0000', u'metadata': {u'result_type': u'recent'}}
    ts = TweetStats()
    
    for i in range(10):
        ts.update(tweet)

    print ts