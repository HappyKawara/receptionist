#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import rospy
import rosparam
import roslib
import smach
import smach_ros
#from fmmmod import FeatureFromVoice, FeatureFromRecog,  LocInfo, SaveInfo
from std_msgs.msg import Float64
from happymimi_msgs.srv import SimpleTrg, StrTrg
from happymimi_navigation.srv import NaviLocation, NaviCoord
#音声
import sp_receptionist as sp

file_path = roslib.packages.get_pkg_dir('happymimi_teleop') + '/src/'
sys.path.insert(0, file_path)
from base_control import BaseControl
# speak
tts_srv = rospy.ServiceProxy('/tts', StrTrg)
# wave_play
wave_srv = rospy.ServiceProxy('/waveplay_srv', StrTrg)

class MoveInitalPosition(smach.State):#ゲストの検出のための位置へ移動
    def __init__(self):
        smach.State.__init__(self,outcomes = ['move_finish']
                             )
        self.gen_coord_srv = rospy.Serviceproxy('/human_coord_generator', SimleTrg)
        #self.ap_srv = rospy.ServiceProxy('/approach_person_server', StrTrg)
        self.navi_srv = rospy.ServiceProxy('navi_location_Server', NaviLocation)
        self.head_pub = rospy.Publisher('/servo/head',Float64, queue_size = 1)
        self.bc = BaseControl()

    def execute(self,userdata):
        rospy.loginfo("Executing state:MOVE_INITAL_POSITION")
        guest_num = userdata.g_count_in
        if guest_num == 1:
            self.navi_srv('inital position')
            self.bc.rotateAngle(,0.2)#入り口の方を向く
            rospy.sleep(0.5)
        elif guest_num == 0:
            tts_srv("start receptionist")
        return 'move_finish'

class DiscoverGuests(smach.State):#ゲストの検出、受付
    def __init__(self):
        smach.State.__init__(self, outcomes = ['discover_finish']
                             )
        self.ap_srv = self.rospy.ServiceProxy('/approach_person_server', StrTrg)
        self.head_pub = rospy.ServiceProxy('/servo/head',Float64, queue_size = 1)

    def execute(self,userdata):
        rospy.loginfo("Executing state:DISCOVERGUESTS")
        '''
        ゲストの検出
        self.ap_srv()
        '''
        wave_srv('/receptionist/hello')
        rospy.sleep(0.5)
        get_feature = sp.GetFeature()
        name = get_feature.getName()
        drink = get_feature.getFavoriteDrink()
        age = get_feature.getAge()#画像認識で可能なら要変更
        wave_srv("/receptionist/ty")
        rospy.sleep(0.5)
        return 'discover_finish'

class IntroduceGuests(smach.State):#オーナーのもとへ移動、ゲストの紹介
    def __init__(self):
        smach.State.__init__(self, outcomes = ['introduce_finish'],
                             input_keys = ['g_count_in']
                             )
        self.navi_srv = rospy.ServiceProxy('navi_location_Server', NaviLocation)
        self.arm_srv = rospy.ServiceProxy('/servo/arm', StrTrg)
        self.bc = BaseControl()

    def execute(self,userdata):
        rospy.loginfo("Executing state:INTRODUCE_GUESTS")
        guest_num = userdata.g_count_in
        self.navi_srv('orner')
        '''
        ゲストの方を指す
        self.bc.rotateAngle(,0.2)
        self.arm_srv('origin')
        '''
        introduce = sp.IntroduceOfGuests()
        introduce.main(guest_num)
        return 'introduce_finish'

class GuideGuests(smach.State):#ゲストのガイド
    def __init__(self):
        smach.State.__init__(self, outcomes = ['guide_finish','all_finish'],
                             input_keys = ['g_count_in'],
                             output_keys =  ['g_count_out'])
        with open(file_path,mode="rb") as f:
            self.feature_dic = pickle.load(f)
        self.bc = BaseControl()
        self.arm_srv = rospy.ServiceProxy('/servo/arm', StrTrg)

    def execute(self, userdata):
        rospy.loginfo("Executing state:GUIDE_GUESTS")
        guest_num = userdata.g_count_in
        if guest_num == 0:
            '''
            空いている椅子を指す
            self.bc.rotateAngle(,0.2)
            self.arm_srv('origin')
            '''
            wave_srv("")#("Please sit in this chair.")
            guest_num += 1
            userdata.g_count_out = guest_num
            return 'guide_finish'
        elif guest_num == 1:#年齢順に
            if self.feature_dic["guest1"]["age"] < self.feature_dic["guest2"]["age"]:
                '''
                空いている椅子を指す（ゲスト１に座らせる）
                '''
                tts_srv("Hi, " + self.feature_dic["guest2"]["name"] +",Please sit in this chair.")
                '''
　　　　　　　　もともとゲスト１が座っていた椅子を指す
                '''
                tts_srv("Hi, " + self.feature_dic["guest1"]["name"] +",Please sit in this chair.")
            else:
                '''
                空いている椅子を指す
                '''
                tts_srv("Hi, " + self.feature_dic["guest1"]["name"] +",Please sit in this chair.")
            return 'all_finish'

if __name__ == '__main__':
    rospy.init_node('receptionist_master')
    rospy.loginfo("Start receptionist")
    sm_top = smach.StateMachine(outcomes = ['finish_sm_top'])
    sm_top.userdata.guest_count = 0
    with sm_top:
        smach.StateMachine.add(
                'MOVE_INITAL_POSITION',
                MoveInitalPosition(),
                transitions = {'move_finish':'DISCOVERGUESTS_GUEST'},
                remapping = {'g_count_in':'guest_count'})

        smach.StateMachine.add(
                'DISCOVERGUESTS_GUEST',
                DiscoverGuests(),
                transitions = {'discover_finish':'INTRODUCE_GUESTS'},
                remapping = {'g_count_in':'guest_count'})

        smach.StateMachine.add(
                'INTRODUCE_GUESTS',
                IntroduceGuests(),
                transitions = {'introduce_finish':'GUIDE_GUESTS'},
                remapping = {'future_out':'guest_future',
                             'g_count_in':'guest_count'})

        smach.StateMachine.add(
                'GUIDE_GUESTS',
                GuideGuests(),
                transitions = {'guide_finish':'MOVE_INITAL_POSITION',
                               'all_finish':'finish_sm_top'},
                remapping = {'g_count_in':'guest_count',
                             'g_count_out':'guest_count'})

    outcome = sm_top.execute()

