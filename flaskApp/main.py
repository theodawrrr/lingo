from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_assets import Environment, Bundle
import tweepy

import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
from flask import Markup
from flask import jsonify

        #data created
        #twitterpost text
        #language
        #spelling score

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '045f300f774941f986881338f7b42196',
}
noTweets=20

@app.route("/")
def main_start():
    return render_template('/index.html')

@app.route("/get_friends")
def get_friends():
    name = request.args.get('name', 0, type=str)
    auth = tweepy.OAuthHandler("4demSjUhdVopc5p2IH1rlZPI9", "c3zPuNUjOvfreAxIdwgPTbsx3OJnvNY595VC0lmbs09PcNUtgm")
    auth.set_access_token("391666744-uoByvtlyK64IYKQGiNJO7St7rl1TnGUfRDggdYua", "D0VqdC8iXW0N6YEJLPk6YYYsmiSe29p7hgSvFiBaGEAXI")
    api = tweepy.API(auth)  
    friends=[]
    print(name)
    for follower in api.followers_ids(name):
        friends.append(api.get_user(follower).screen_name)

    #for page in tweepy.Cursor(api.followers_ids, screen_name=name).items():
    #   friends.append(page.screen_name)

    #friends=api.followers(id=name) 
    #friendArr=[]
    #for f in friends:
    #    print(f['screen_name'])
    #    friendArr.append(f['screen_name'])
    print(friends) 
    return jsonify(friends[0:3]) #return top 3 friends


@app.route('/get_tweets')
def get_tweets():
    name = request.args.get('name', 0, type=str)
    print("hello",name)
    auth = tweepy.OAuthHandler("4demSjUhdVopc5p2IH1rlZPI9", "c3zPuNUjOvfreAxIdwgPTbsx3OJnvNY595VC0lmbs09PcNUtgm")
    auth.set_access_token("391666744-uoByvtlyK64IYKQGiNJO7St7rl1TnGUfRDggdYua", "D0VqdC8iXW0N6YEJLPk6YYYsmiSe29p7hgSvFiBaGEAXI")

    api = tweepy.API(auth)

    #how to you compare to friends api.friends
    #user= request.form['twitterHandle']
    #"BecksTSimpson" #"hacksmiths"#


    public_tweets = api.user_timeline(id=name,count=noTweets)
    
    #print str(public_tweets[0])
    tweetInformation=[]
    print(public_tweets)
    for i, tweet in enumerate(public_tweets):
        
        tw=str(tweet.text) #created_at
        
        
        
        #print(tweet)
        #print (tw[0:2])
        if(tw[0:2]== "RT"):
            #print( "RETWEET")
            continue
        
        words= tw.split(" ")
        toremove=[]
        for u,word in enumerate(words):
            #print (str(word))
            if "https" in word or "#" in word or "@" in word:
                words[u]=""
            
        twitterPost= " ".join(w for w in filter(lambda x: x!="", words))
        twitterPost=twitterPost.replace("\n", " ")
        twitterPost= twitterPost.rstrip('\n')
        if(twitterPost.strip()==""):
            print("STRING IS ONLY SPACES")
            continue
        #print("twitterPost:  ", twitterPost)
        tweetInformation.append([])
        index= len(tweetInformation)-1



        tweetInformation[index].append(str(tweet.created_at))
        tweetInformation[index].append(twitterPost)
    #wINDOWS LANGUAGE DETECT
    #https://[location].api.cognitive.microsoft.com/text/analytics/v2.0/languages[?numberOfLanguagesToDetect]


        #Get sentence language
        print(" The twitter post trying to send is", twitterPost)
        body={ "documents": [{ "id": "string","text":twitterPost}]}
        data_json = json.dumps(body)    
        try:
            conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
            conn.request("POST", "/text/analytics/v2.0/languages", data_json, headers)
            response = conn.getresponse()
            data = response.read()
            data= json.loads(data)
            print("the data is", data)

            langType=data["documents"][0]["detectedLanguages"][0]["name"] #langage type
            tweetInformation[index].append(langType)
            conn.close()
        except Exception as e:
            print("The error is [Errno {0}] {1}".format(e.errno, e.strerror))

        #Get spelling score
        wordcount = len(list(filter(lambda x: x!="", words)))
        print(wordcount)
        params = {'mkt': 'en-US', 'mode': 'spell', 'text': twitterPost}
        key = '32ed427d493d4b3da7805d4cb9626855'
        host = 'api.cognitive.microsoft.com'
        path = '/bing/v7.0/spellcheck'
        headers2 = {'Ocp-Apim-Subscription-Key': key,
        'Content-Type': 'application/x-www-form-urlencoded'}
        conn2 = http.client.HTTPSConnection(host)
        params = urllib.parse.urlencode (params)
        conn2.request ("POST", path, params, headers2)
        response2 = conn2.getresponse()
        print(response2)
        print(response2.read)
        response2 = response2.read()
        response2 = json.loads(response2)
        conn2.close()
        if "flaggedTokens" in response2:
            print(response2["flaggedTokens"])
            tokens = len(response2["flaggedTokens"])
            score = (int(wordcount) - int(tokens))/int(wordcount)
        else:
            score= 1
        print("The number of correctly spelt words is: " + str(score) + " out of " + str(wordcount) +"!")
        tweetInformation[index].append(score)


    print (tweetInformation)
    tweetInformation.reverse()
    returnData={"spellings": [x[3] for x in tweetInformation], "dates": [x[0] for x in tweetInformation], "posts": [x[1] for x in tweetInformation], "languages": [x[2] for x in tweetInformation]}
    return jsonify(returnData)


@app.route('/start_twitter',  methods=['POST'])
def start_twitter():
    #fetch twitter data


    auth = tweepy.OAuthHandler("4demSjUhdVopc5p2IH1rlZPI9", "c3zPuNUjOvfreAxIdwgPTbsx3OJnvNY595VC0lmbs09PcNUtgm")
    auth.set_access_token("391666744-uoByvtlyK64IYKQGiNJO7St7rl1TnGUfRDggdYua", "D0VqdC8iXW0N6YEJLPk6YYYsmiSe29p7hgSvFiBaGEAXI")

    api = tweepy.API(auth)

    #how to you compare to friends api.friends
    user= request.form['twitterHandle']
    #"BecksTSimpson" #"hacksmiths"#


    public_tweets = api.user_timeline(id=user,count=noTweets)
    
    #print str(public_tweets[0])
    tweetInformation=[]

    for i, tweet in enumerate(public_tweets):
        
        tw=str(tweet.text) #created_at
        
        
        
        #print(tweet)
        #print (tw[0:2])
        if(tw[0:2]== "RT"):
            #print( "RETWEET")
            continue
        
        words= tw.split(" ")
        toremove=[]
        for u,word in enumerate(words):
            #print (str(word))
            if "https" in word or "#" in word or "@" in word:
                words[u]=""
            
        twitterPost= " ".join(w for w in filter(lambda x: x!="", words))
        twitterPost=twitterPost.replace("\n", " ")
        twitterPost= twitterPost.rstrip('\n')
        if(twitterPost.strip()==""):
            print("STRING IS ONLY SPACES")
            continue
        #print("twitterPost:  ", twitterPost)
        tweetInformation.append([])
        index= len(tweetInformation)-1



        tweetInformation[index].append(str(tweet.created_at))
        tweetInformation[index].append(twitterPost)
    #wINDOWS LANGUAGE DETECT
    #https://[location].api.cognitive.microsoft.com/text/analytics/v2.0/languages[?numberOfLanguagesToDetect]


        #Get sentence language
        print(" The twitter post trying to send is", twitterPost)
        body={ "documents": [{ "id": "string","text":twitterPost}]}
        data_json = json.dumps(body)    
        try:
            conn = http.client.HTTPSConnection('northeurope.api.cognitive.microsoft.com')
            conn.request("POST", "/text/analytics/v2.0/languages", data_json, headers)
            response = conn.getresponse()
            data = response.read()
            data= json.loads(data)
            print("the data is", data)

            langType=data["documents"][0]["detectedLanguages"][0]["name"] #langage type
            tweetInformation[index].append(langType)
            conn.close()
        except Exception as e:
            print("The error is [Errno {0}] {1}".format(e.errno, e.strerror))

        #Get spelling score
        wordcount = len(list(filter(lambda x: x!="", words)))
        print(wordcount)
        params = {'mkt': 'en-US', 'mode': 'spell', 'text': twitterPost}
        key = '32ed427d493d4b3da7805d4cb9626855'
        host = 'api.cognitive.microsoft.com'
        path = '/bing/v7.0/spellcheck'
        headers2 = {'Ocp-Apim-Subscription-Key': key,
        'Content-Type': 'application/x-www-form-urlencoded'}
        conn2 = http.client.HTTPSConnection(host)
        params = urllib.parse.urlencode (params)
        conn2.request ("POST", path, params, headers2)
        response2 = conn2.getresponse()
        print(response2)
        print(response2.read)
        response2 = response2.read()
        response2 = json.loads(response2)
        conn2.close()
        if "flaggedTokens" in response2:
            print(response2["flaggedTokens"])
            tokens = len(response2["flaggedTokens"])
            score = (int(wordcount) - int(tokens))/int(wordcount)
        else:
            score= 1
        print("The number of correctly spelt words is: " + str(score) + " out of " + str(wordcount) +"!")
        tweetInformation[index].append(score)


    print (tweetInformation)
    tweetInformation.reverse()
    #for tweet in public_tweets:
    #    print (tweet.text)
    return render_template('/main.html', user=user,spellings= [x[3] for x in tweetInformation], dates= [x[0] for x in tweetInformation], posts= [x[1] for x in tweetInformation], languages= [x[2] for x in tweetInformation])

if __name__ == "__main__":
    app.run(port=8000)
  