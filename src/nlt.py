#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
import os
from os import path
from happymimi_msgs.srv import StrTrg
from happymimi_voice_msgs.srv import SpeechToText
import sys
import rospy
import random
from nltk.tag.stanford import StanfordPOSTagger
import re
nltk_path=path.expanduser('~/main_ws/src/happymimi_voice/config/dataset')
pos_tag = StanfordPOSTagger(model_filename = nltk_path + "/stanford-postagger/models/english-bidirectional-distsim.tagger",
                            path_to_jar = nltk_path + "/stanford-postagger/stanford-postagger.jar")

'''
self.feature_dic = {"guest1":{"name":"","drink":"","age":""},
                "guest2":{"name":"","drink":"","age":""}}
'''

file_path=os.path.expanduser('~/main_ws/src/receptionist/config/guest_feature.pkl')
class GetFeature():
    def __init__(self):
        print('Waiting for tts and stt_server')
        '''
        rospy.wait_for_service('/tts')
        rospy.wait_for_service('/stt_server')
        self.stt=rospy.ServiceProxy('/stt_server',SpeechToText)
        self.tts=rospy.ServiceProxy('/tts', StrTrg)
        with open(file_path,mode="rb") as f:
            self.feature_dic = pickle.load(f)
        '''

    def savePickle(self,feature_type,feature):
        if self.feature_dic["guest1"][feature_type]:
            self.feature_dic["guest2"][feature_type] = feature
        else:
            self.feature_dic["guest1"][feature_type] = feature
        with open(file_path,mode="wb") as f:
            pickle.dump(self.feature_dic,f)

    def getName(self):
        n = 0
        #print(''.join(re.findall(r'\d+', self.feature_dic["guest1"]["age"])))
        while n < 2:
            name = ''
            name2 = ''
            #self.tts("What is your name?")
            #ans = self.stt().result_str
            ans = "i'm mike."
            #名前だけ取り出すようにする
            pos = pos_tag.tag(ans.split())
            print(pos)
            for i,p in enumerate(pos):
                if p[1] == 'NNP':
                    name = p[0]
                if ((p[1] == 'NN')and(p[0] != 'name')):
                    name2 = p[0]
                if ((p[1] == 'ADD')and(p[0] != 'name')):
                    name2 = p[0]
                if p[0] == "i'm":
                    name = pos[i+1][0]
            if not name:
                name =name2
            #self.tts("Are you" + name + "? please answer yes or no.")
            print(pos)
            print(ans)
            print(name)
            rospy.sleep(0.5)
            #yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            print(yes_no.result_str)
            if ({"yes","yeah","yet",""} & set(yes_no.result_str.split())):
                self.savePickle("name",name)
                n = 2
                print('true')
            else:
                if n == 1:
                    self.savePickle("name","None")
                n+=1

    def getFavoriteDrink(self):
        n = 0
        while n < 2:
            self.tts("What is your favorite drink?")
            ans = self.stt().result_str
            #ans = "my favorite drink is coffee."
            #飲み物だけ取り出すようにする
            pos = pos_tag.tag(ans.split())
            drink = ""
            print(pos)
            for p in pos:
                if p[1] == 'NN':
                    if p[0] != 'drink':
                        drink = drink + p[0]
                elif p[1] == 'NNP':
                    drink = drink + p[0]
            drink = drink.replace('.','')
            self.tts("your favorite drink is " + drink + ". Is this ok? please answer yes or no.")
            print(drink)
            rospy.sleep(0.5)
            yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            print(yes_no.result_str)
            if ({"yes","yeah","yet",""} & set(yes_no.result_str.split())):
                print(("yes","yeah",yes_no.result_str.split()))
                self.savePickle("drink",drink)
                n = 2
                print('true')
            else:
                if n == 1:
                    self.savePickle("drink","None")
                n+=1

    def getAge(self):
        n = 0
        while n < 2:
            self.tts("How old are you?")
            ans = self.stt().result_str#年齢だけ取り出すようにする
            self.tts("You are" + ans + ". Is this ok? please answer yes or no.")
            ans = ans.replace('.','')
            yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            if ({"yes","yeah","yet",""} & set(yes_no.result_str.split())):
                self.savePickle("age",ans)
                n = 2
                print('true')
            else:
                if n == 1:
                    self.savePickle("age","None")
                n+=1

class IntroduceOfGuests():
    def __init__(self):
        self.tts=rospy.ServiceProxy('/tts', StrTrg)

    def main(self,number):#ゲストの特徴を伝える
        if number == 0:
            guest_number = 'guest1'
        else:
            guest_number = 'guest2'
        with open(file_path,mode="rb") as f:
            self.feature_dic = pickle.load(f)
        self.tts("guest's name is " +self.feature_dic[guest_number]["name"])
        self.tts(self.feature_dic[guest_number]["name"] +"'s favorite drink is "
                 + self.feature_dic[guest_number]["drink"])


class GuideGuests():
    def __init__(self):
        self.tts=rospy.ServiceProxy('/tts', StrTrg)
        with open(file_path,mode="rb") as f:
            self.feature_dic = pickle.load(f)

    def main(self):#席の移動をさせる
        self.tts("Hi, " + self.feature_dic["guest1"]["name"] +",Please sit in this chair.")
        self.tts("Hi, " + self.feature_dic["guest2"]["name"] +",Please sit in this chair.")

if __name__ == "__main__":
    #print("a")
    g = GetFeature()
    g.getName()
    #g.getFavoriteDrink()
    
