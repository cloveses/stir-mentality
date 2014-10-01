#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

class MySqliteDb(object):
    """Sqlite3 Db Class"""
    def __init__(self, dbname="mys.db"):
        self.dbname = dbname
        self.con = None
        self.curs = None

    def getCursor(self):
        self.con = sqlite3.connect(self.dbname)
        if self.con:
            self.curs = self.con.cursor()

    def closeDb(self):
        if self.curs:
            self.curs.close()
        if self.con:
            self.con.commit()
            self.con.close()

    def __enter__(self):
        self.getCursor()
        return self.curs

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            print("Exception has generate: ",exc_val)
            print("Sqlite3 execute error!")
        self.closeDb()

def initDb(db):
    crtSql = (
        '''
        create table stu_sbjct
        (id integer primary key autoincrement not null,
        title varchar(500) not null,
        qstn text,
        openothr integer default 0)
        ''',
        '''
        create table stu_answrs(
        id integer primary key autoincrement not null,
        sbjct_id integer,
        stu_id integer,
        answr text,
        answr_time timestamp default current_timestamp
            )
        ''',
        '''
        create table stds
        (
        id integer primary key autoincrement not null,
        name varchar(8),
        psswd varchar(256),
        usertype integer
            )
        ''',
        '''
        create table ask_hlps
        (
        id integer primary key autoincrement not null,
        stu_id integer,
        qstn text,
        ask_time  timestamp default current_timestamp
            )
        ''',
        '''
        create table hlp_answrs
        (
        id integer primary key autoincrement not null,
        ask_id integer,
        hlper_id integer,
        answr text,
        answr_time  timestamp default current_timestamp
            )
        '''
        )
    for sql in crtSql:
        db.execute(sql)

class AskHelps(object):
    def __init__(self,id=0,stu_id=0,qstn=''):
        self.id = id
        self.stu_id =stu_id
        self.qstn =qstn

    def getLastQstns(self,totals=20):
        with MySqliteDb() as db:
            res = db.execute("select ask_hlps.id,ask_hlps.stu_id,ask_hlps.qstn,ask_hlps.ask_time,stds.name from ask_hlps,stds where stds.id=ask_hlps.stu_id order by ask_time desc limit ?",(totals,))
            re = res.fetchall()
        return re

    def save(self):
        re = 0
        if self.stu_id and self.qstn:
            with MySqliteDb() as db:
                res = db.execute("insert into ask_hlps (stu_id,qstn) values (?,?)",(self.stu_id,self.qstn))
                re = res.rowcount
        return re

class HlpAnswrs(object):
    def __init__(self,ask_id=0,hlper_id=0,answr=''):
        self.ask_id = ask_id
        self.hlper_id = hlper_id
        self.answr = answr

    def save(self):
        re = 0
        if self.ask_id and self.hlper_id and self.answr:
            with MySqliteDb() as db:
                res = db.execute("insert into hlp_answrs (ask_id,hlper_id,answr) values (?,?,?)",
                    (self.ask_id,self.hlper_id,self.answr))
                re = res.rowcount
        return re

    def getAnswrs(self,ask_id):
        with MySqliteDb() as db:
            res = db.execute(
                '''
                select hlp_answrs.id,hlp_answrs.answr,stds.name from hlp_answrs,stds
                where hlp_answrs.ask_id=? and hlp_answrs.hlper_id=stds.id
                order by hlp_answrs.answr_time
                ''',
                (ask_id,)
                )
            re = res.fetchall()
        return re


class StuSbjct(object):
    """学习主题 stu_sbjct"""
    def __init__(self,id=0, title='',qstn=''):
        self.title=title
        self.qstn = qstn
        self.id = id

    def save(self):
        if self.title and self.qstn:
            with MySqliteDb() as db:
                db.execute(
                    "insert into stu_sbjct (title,qstn) values (?,?)",
                    (self.title,self.qstn)
                    )
            return True

    def getSbjcts(self):
        with MySqliteDb() as db:
            res = db.execute("select * from stu_sbjct")
            res = res.fetchall()
        return res

    def setOpenOthr(self,sbjct_id):
        with MySqliteDb() as db:
            res = db.execute("select * from stu_sbjct where id=?",(sbjct_id,))
            res = res.fetchone()
            flag = 0 if res[3] else 1
            res = db.execute("update stu_sbjct set openothr=? where id=?",(flag,sbjct_id))
            re = res.rowcount
        return re

class StuAnswr(object):
    """学生回答 StuAnswrs"""
    def __init__(self, id=0,sbjct_id=0,stu_id=0,answr=''):
        self.id = id
        self.sbjct_id = sbjct_id
        self.stu_id = stu_id
        self.answr = answr

    def save(self):
        if self.sbjct_id and self.stu_id and self.answr:
            with MySqliteDb() as db:
                db.execute(
                    "insert into stu_answrs (sbjct_id,stu_id,answr) values (?,?,?)",
                    (self.sbjct_id,self.stu_id,self.answr)
                    )
            return True
        return False
        
    def getAnswrs(self,sbjct_id):
        with MySqliteDb() as db:
            res = db.execute("select stu_answrs.id,stu_answrs.sbjct_id,stds.name,stu_answrs.answr,stu_answrs.answr_time from stu_answrs,stds where stu_answrs.sbjct_id=? and stu_answrs.stu_id=stds.id order by answr_time",(sbjct_id,))
            res = res.fetchall()
        return res

    def getSelfAnswr(self,sbjct_id,stu_id):
        with MySqliteDb() as db:
            res = db.execute("select stu_answrs.id,stu_answrs.sbjct_id,stds.name,stu_answrs.answr,stu_answrs.answr_time from stu_answrs,stds where stu_answrs.sbjct_id=? and stu_answrs.stu_id=? and stu_answrs.stu_id=stds.id order by answr_time",(sbjct_id,stu_id))
            res = res.fetchall()
        return res

    def isAnswred(self,stu_id,sbjct_id):
        with MySqliteDb() as db:
            res =db.execute("select * from stu_answrs where stu_id=? and sbjct_id=?",(stu_id,sbjct_id))
            res = res.fetchall()
        if res:
            return True
        else:
            return False
        

class Stu(object):
    """class for stds"""
    def __init__(self,id=0, name='',psswd='',usertype=0):
        self.id = id
        self.name = name
        self.psswd = psswd
        self.usertype = usertype

    def save(self):
        if self.name and self.psswd:
            with MySqliteDb() as db:
                db.execute(
                    "insert into stds (name,psswd,usertype) values (?,?,?)",
                    (self.name,self.psswd,self.usertype)
                    )
            return True

    def isRgstr(self):
        with MySqliteDb() as db:
            res = db.execute(
                "select * from stds where name=? and psswd=?",
                (self.name,self.psswd)
                )
            res = res.fetchall()
        if res:
            return res[0]
        else:
            return False

    def getStuName(self,stu_id):
        with MySqliteDb() as db:
            res = db.execute(
                "select * from stds where id=?",(stu_id,)
                )
            res = res.fetchall()
        if res:
            return res[1]
        else:
            return ''

def setupDb():
    if not os.path.exists('mys.db'):
        with MySqliteDb() as db:
            initDb(db)
            print("Sqlite3 Db initialize success!")

if __name__ == '__main__':
    # with MySqliteDb() as db:
        # initDb(db)
        # print('Sqlite3 Db initialize success!')
        # db.execute("delete from ask_hlps;")
        # db.execute("insert into stds (name,psswd) values (?,?)",('aaa','bbbbb'))
        # res = db.execute("select * from stu_sbjct")
        # print(res.fetchall())
        # res = db.execute("select * from hlp_answrs")
        # print(res.fetchall())
        # db.execute("alter table stds add column usertype integer default 0")
        # pass
    print('Sqlite3 testing success!')
