# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

import naminggamesal as ngal

# Create your models here.

import json


class Word(models.Model):
    word = models.CharField(max_length=200)
    #experiment = models.ManyToManyField(Experiment,null=True)
    def __str__(self):
        return self.word

class Role(models.Model):
    role = models.CharField(max_length=10)
    def __str__(self):
        return self.role

class Meaning(models.Model):
    #experiment = models.ManyToManyField(Experiment,null=True)
    #meaning = models.IntegerField()
    meaning = models.CharField(max_length=100)
    def __str__(self):
        return self.meaning

class XpConfig(models.Model):
    xp_config = models.CharField(max_length=2000)
    usage = models.IntegerField(default=0)
    def __str__(self):
        return self.xp_config


class Experiment(models.Model):
    xp_config = models.ForeignKey(XpConfig, on_delete=models.CASCADE)
    xp_uuid = models.CharField(max_length=200,default='')
    user_agent_uuid = models.CharField(max_length=200,default='')
    interaction_counter = models.IntegerField(default=0)
    max_interaction = models.IntegerField(default=10)
    exit_value = models.FloatField(default=0)
    meanings = models.ManyToManyField(Meaning)
    words = models.ManyToManyField(Word)
    def __str__(self):
        return str(self.xp_uuid) + ' ' + str(self.xp_config.xp_config)

    def get_xp(self):
        db = ngal.ngdb.NamingGamesDB()
        if self.xp_uuid == '':
            xp = db.get_experiment(**json.loads(self.xp_config.xp_config))
            self.xp_uuid = xp.uuid
            self.save()
        else:
            xp = db.get_experiment(xp_uuid=self.xp_uuid)
        return xp

    def continue_xp(self,steps=1):
        xp = self.get_xp()
        xp.continue_exp(dT=steps)
        #self.interaction_counter += steps
        self.interaction_counter = xp._T[-1]
        self.save()

    def update_results(self):
        xp = self.get_xp()
        gr = xp.graph(method='srtheo')
        if gr._Y[0]:
            self.exit_code = gr._Y[0][-1]
        self.save()

    def get_currentgame_json(self):
        filename = './data/current_game_info/'+self.xp_uuid+'.txt'
        with open(filename,'r') as f:
            currentgame_json = json.loads(f.read())
        return currentgame_json

    def save_currentgame_json(self,currentgame_json):
        filename = './data/current_game_info/'+self.xp_uuid+'.txt'
        with open(filename,'w') as f:
            f.write(json.dumps(currentgame_json))

    def get_user_agent_uuid(self):
        if self.user_agent_uuid == '':
            xp = self.get_xp()
            self.user_agent_uuid = xp._poplist.get_last()._agentlist[0]._id
        self.save()
        return self.user_agent_uuid

    def get_last_bool_succ(self):
        xp = self.get_xp()
        return xp._poplist.get_last()._lastgameinfo[3]

    def update_words(self):
        xp = self.get_xp()
        ag = xp._poplist.get_last()._agentlist[0]
        w_list = sorted(ag._vocabulary.get_accessible_words())
        self.words.clear()
        for w in w_list:
            obj_list = Word.objects.filter(word=w)
            if len(obj_list) == 0:
                w_obj = Word.objects.create(word=w)
            else:
                w_obj = obj_list[0]
            self.words.add(w_obj)
        self.save()
    
    def update_meanings(self):
        xp = self.get_xp()
        ag = xp._poplist.get_last()._agentlist[0]
        m_list = sorted(ag._vocabulary.get_accessible_meanings())
        print m_list
        self.meanings.clear()
        for m in m_list:
            obj_list = Meaning.objects.filter(meaning=str(m))
            #print str(obj_list)
            if len(obj_list) == 0:
                m_obj = Meaning.objects.create(meaning=str(m))
                print 'bla'
            else:
                m_obj = obj_list[0]

            self.meanings.add(m_obj)
            print m_obj
        self.save()

class PastInteraction(models.Model):
    #meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    #word = models.ForeignKey(Word, on_delete=models.CASCADE)
    #bool_succ = models.IntegerField()
    #role = models.ForeignKey(Role, on_delete=models.CASCADE)
    meaning = models.IntegerField()
    word = models.CharField(max_length=20)
    bool_succ = models.IntegerField()
    time_id = models.IntegerField()
    role = models.CharField(max_length=20)
    experiment = models.ForeignKey(Experiment,null=True)#, on_delete=models.CASCADE, default=Experiment.objects.all()[0])
    #xp_uuid = models.CharField(max_length=200,default = '')
    def __str__(self):
        return str(self.meaning) + ' ' +str(self.word) + ' ' +str(self.role) + ' ' + str(self.bool_succ)

