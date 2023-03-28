#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
from os import path
from happymimi_msgs.srv import StrTrg
from happymimi_voice_msgs.srv import SpeechToText
import sys
import rospy
import random
'''
self.feature_dic = {"guest1":{"name":"","drink":"","age":""},
                "guest2":{"name":"","drink":"","age":""}}
'''
file_path = ""
class GetFeature():
    def __init__(self):
        print('Wahing for tts and stt_server')
        rospy.wait_for_service('/tts')
        rospy.wait_for_service('/stt_server')
        self.stt=rospy.ServiceProxy('/stt_server',SpeechToText)
        self.tts=rospy.ServiceProxy('/tts', StrTrg)
        with open(file_path,mode="rb") as f:
            self.feature_dic = pickle.load(f)

    def savePickle(self,feature_type,feature):
        if self.feature_dic["guest2"][feature_type]:
            self.feature_dic["guest1"][feature_type] = feature
        else:
            self.feature["guest2"][feature_type] = feature
        with open(file_path,mode="wb") as f:
            pickle.dump(self.feature_dic,f)

    def getName(self):
        n = 0
        while n < 2:
            self.tts("What is your name?")
            ans = self.stt().result_str#名前だけ取り出すようにする
            self.tts("Are you" + ans + "? please answer yes or no.")
            yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            if "yes" in yes_no:
                savePickle("name",ans)
                n = 2
            else:
                if n == 1:
                    savePickle("name","None")
                n+=1

    def getFavoriteDrink(self):
        n = 0
        while n < 2:
            self.tts("What is your favorite drink?")
            ans = self.stt().result_str#飲み物だけ取り出すようにする
            self.tts("your favorite drink is" + ans + ". Is this ok? please answer yes or no.")
            yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            if "yes" in yes_no:
                savePickle("drink",ans)
                n = 2
            else:
                if n == 1:
                    savePickle("drink","None")
                n+=1

    def getAge(self):
        n = 0
        while n < 2:
            self.tts("How old are you?")
            ans = self.stt().result_str#年齢だけ取り出すようにする
            self.tts("You are" + ans + ". Is this ok? please answer yes or no.")
            yes_no = self.stt(short_str=True,context_phrases=["yes","no"],boost_value=20.0)
            if "yes" in yes_no:
                savePickle("age",ans)
                n = 2
            else:
                if n == 1:
                    savePickle("age","None")
                n+=1

class IntroductionOfGuest():
    def __init__(self):
        self.tts=rospy.ServiceProxy('/tts', StrTrg)

    def main(self,guest_number):#ゲストの特徴を伝える
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


