#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os,signal,re
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler, Application,authenticated
from tornado.escape import url_escape,json_encode
# from db_mgr import MySqliteDb as myDb
from db_mgr import Stu,StuSbjct,StuAnswr,AskHelps,HlpAnswrs,setupDb,initIpaddr

from mako.template import Template
from mako.lookup import TemplateLookup

CURRENT_PATH = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(CURRENT_PATH,'templates')
print("Templates's path: ",TEMPLATE_PATH)
LOOK_UP = TemplateLookup(directories=[TEMPLATE_PATH,],
    output_encoding='utf-8',encoding_errors='replace',
    input_encoding='utf-8')

class BaseHandler(RequestHandler):
    """ Use mako template system """
    def initialize(self,lookup=LOOK_UP):
        self._lookup = lookup

    def render(self,filename,kwargs={}):
        env_kwargs = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.application.reverse_url)
        env_kwargs.update(kwargs)
        try:
            myTemplate = self._lookup.get_template(filename)
            self.finish(myTemplate.render(**env_kwargs))
        except:
            print('Did not find template file:',filename)
            self.send_error(404)

    def get_current_user(self):
        return self.get_secure_cookie('name')
        

setttings = {
    "static_path":os.path.join(CURRENT_PATH,'static'),
    # "debug":True,
    "cookie_secret":"!#%^&&**((JHGHUUkjhlihli+_))(?><:HJKGgue$^&&*",
}
mgr_code="mypassword" #管理员注册附加验证码
LINE_LEN = 38

class HelloHandler(BaseHandler):
    """ index page """
    def get(self,sbjct_id):
        info = self.get_argument("info",default='')
        all_sbjcts = StuSbjct().getSbjcts()
        name = self.get_secure_cookie('name')
        stu_id = self.get_secure_cookie('id')
        usertype = self.get_secure_cookie('usertype')
        all_hlp_self = self.getHlps()
        if name:
            name = name.decode('utf-8')
            stu_id = stu_id.decode('utf-8')
            usertype = 0 if not usertype else int(usertype.decode('utf-8'))
        crrnt_sbjct = self.getCrrntSbjct(all_sbjcts,sbjct_id) if all_sbjcts else ()
        if crrnt_sbjct and (crrnt_sbjct[3] or usertype):
            all_answrs = StuAnswr().getAnswrs(crrnt_sbjct[0])
        else:
            if crrnt_sbjct and name:
                all_answrs = StuAnswr().getSelfAnswr(crrnt_sbjct[0],int(stu_id))
            else:
                all_answrs = []
        self.render('index.html',dict(stu_id=stu_id,name=name,usertype=usertype,
            all_sbjcts=all_sbjcts,crrnt_sbjct=crrnt_sbjct,info=info,
            all_answrs=all_answrs,all_hlp_self=all_hlp_self))

    def post(self,sbjct_id):
        all_sbjcts = StuSbjct().getSbjcts()
        crrnt_sbjct = self.getCrrntSbjct(all_sbjcts,sbjct_id) if all_sbjcts else ()
        name = self.get_argument("name",default='')
        psswd = self.get_argument("psswd",default='')
        if name and psswd:
            re = Stu(name=name,psswd=psswd,ipaddr=self.request.remote_ip).isRgstr()
            # print(self.request.remote_ip)
            if re:
                self.set_secure_cookie('name',str(re[1]))
                self.set_secure_cookie('id',str(re[0]))
                self.set_secure_cookie('usertype',str(re[3]))
                if crrnt_sbjct and (crrnt_sbjct[3] or re[3]):
                    all_answrs = StuAnswr().getAnswrs(crrnt_sbjct[0])
                elif crrnt_sbjct:
                    all_answrs = StuAnswr().getSelfAnswr(crrnt_sbjct[0],int(re[0]))
                else:
                    all_answrs = []
                all_hlp_self = self.getHlps()
                self.render('index.html',dict(stu_id=re[0],name=name,usertype=re[3],
                    all_sbjcts=all_sbjcts,crrnt_sbjct=crrnt_sbjct,info='',
                    all_answrs=all_answrs,all_hlp_self=all_hlp_self))
            else:
                self.redirect('/?info=' + url_escape("登录失败!"))
        else:
            self.redirect('/?info=' + url_escape("登录失败!"))

    def getCrrntSbjct(self,all_sbjcts,sbjct_id):
        if (sbjct_id !=''):
            crrnt_sb_id = int(sbjct_id)
            for item in all_sbjcts:
                if item[0]==crrnt_sb_id:
                    crrnt_sbjct = item
                    break
        else:
            crrnt_sbjct = all_sbjcts[0]
        return crrnt_sbjct

    def getHlps(self):
        res = AskHelps().getLastQstns()
        # print(res)
        hlpanswr = HlpAnswrs()
        re = [[item,hlpanswr.getAnswrs(item[0])] for item in res]
        # print(re)
        return re


class TmplTestHdl(BaseHandler):
    """ Template test handler """
    def get(self):
        self.render('a.html',{'name':'aaaaa'})

class SignUpHandler(BaseHandler):

    def get(self):
        msg = self.get_argument('msg',default='')
        self.render('signup.html',dict(msg=msg))

    def post(self):
        para_keys=('name','ps','psbak')
        para_dict={}
        mgr_code_u = self.get_argument('mgr_code',default='')
        if mgr_code_u and mgr_code_u==mgr_code:
            usertype = 1
        else:
            usertype = 0
        for key in para_keys:
            para_dict.update({key:self.get_argument(key,default='')})
        if all(para_dict.values()):
            if para_dict['ps']==para_dict['psbak']:
                astu = Stu(name=para_dict['name'],psswd=para_dict['ps'],usertype=usertype)
                if astu.had_name():
                    self.redirect('/signup?msg='+url_escape("用户名已经被注册!"))
                    return
                astu.save()
                re = Stu(name=para_dict['name'],psswd=para_dict['ps']).isRgstr()
                if re:
                    self.set_secure_cookie('name',str(re[1]))
                    self.set_secure_cookie('id',str(re[0]))
                    self.set_secure_cookie('usertype',str(re[3]))
                self.redirect('/')
            else:
                self.redirect('/signup?msg='+url_escape("密码不匹配"))
        else:
            self.redirect('/signup?msg='+url_escape("参数不全"))

class LogoutHdl(BaseHandler):
    """用户注销"""
    def get(self):
        self.clear_all_cookies()
        self.redirect('/')

class AddQstnHdl(BaseHandler):

    @authenticated
    def post(self):
        title = self.get_argument('title')
        qstn = self.get_argument('qstn')
        qstn = format_html(qstn)
        self.set_header("Content-Type","application/json; charset=UTF-8")
        if title and qstn:
            if StuSbjct(title=title,qstn=qstn).save():
                self.write(json_encode(1))
            else:
                self.write(json_encode(0))
        else:
            return self.write(json_encode(0))
        
class AddAnswrHdl(BaseHandler):
    """保存学生提交答案"""
    @authenticated
    def post(self):
        sbjct_id = int(self.get_argument('sbjct_id'))
        stu_id = int(self.get_argument('stu_id'))
        if StuAnswr().isAnswred(stu_id,sbjct_id):
            self.write(json_encode(2))
        else:
            answr = self.get_argument('answr')
            answr = format_html(answr)
            self.set_header("Content-Type","application/json; charset=UTF-8")
            if sbjct_id and stu_id and answr:
                if StuAnswr(sbjct_id=sbjct_id,stu_id=stu_id,answr=answr).save():
                    self.write(json_encode(1))
                else:
                    self.write(json_encode(0))
            else:
                self.write(json_encode(0))

def format_html(htmlstr):
    htmlstr = htmlstr.strip()
    htmlstr = re.sub(r'\r\n',r'\n',htmlstr)
    htmlstr = re.sub(r'\r',r'\n',htmlstr)
    htmlstr = re.split(r'\n',htmlstr)
    htmlstr = ['<p>'+item+'</p>' for item in htmlstr]
    return re.sub(r' ',"&nbsp;",''.join(htmlstr))

class DispAllAnswrHdl(BaseHandler):
    """ajax 开启／关闭其它同学答案"""
    @authenticated
    def get(self,sbjct_id):
        res = StuSbjct().setOpenOthr(int(sbjct_id))
        self.set_header("Content-Type","application/json; charset=UTF-8")
        if res==1:
            self.write(json_encode(1))
        else:
            self.write(json_encode(0))

class AskHlpHdl(BaseHandler):
    """ajax 保存求助的问题"""
    @authenticated
    def post(self,stu_id):
        stu_id = int(stu_id)
        qstn = self.get_argument('qstn')
        res = 0
        if stu_id and qstn:
            res = AskHelps(stu_id=stu_id,qstn=qstn).save()
        self.set_header("Content-Type","application/json; charset=UTF-8")
        self.write(json_encode(res))

class HelpAnswrHdl(BaseHandler):
    """ajax 保存求助问题的解答与讨论"""
    @authenticated
    def post(self,ask_id,hlper_id):
        ask_id = int(ask_id)
        hlper_id = int(hlper_id)
        answr = self.get_argument('answr')
        res = 0
        if ask_id and hlper_id and answr:
            res = HlpAnswrs(ask_id=ask_id,hlper_id=hlper_id,answr=answr).save()
        self.set_header("Content-Type","application/json; charset=UTF-8")
        self.write(json_encode(res))

class DelAllAnswrHdl(BaseHandler):
    """ajax 删除所有自助问答"""
    @authenticated
    def get(self):
        AskHelps().delAskHlps()
        
def make_app():
    return Application([
        (r"/([0-9]*)", HelloHandler),
        (r"/tmptst",TmplTestHdl),
        (r"/signup",SignUpHandler),
        (r"/logout",LogoutHdl),
        (r"/add_qstn",AddQstnHdl),
        (r"/add_answr",AddAnswrHdl),
        (r"/on_off_answr/([0-9]+)",DispAllAnswrHdl),
        (r"/ask_hlp/([0-9]+)",AskHlpHdl),
        (r"/hlp_answr/([0-9]+)/([0-9]+)",HelpAnswrHdl),
        (r"/del_hlp_data",DelAllAnswrHdl),
        ],**setttings)

def stop_serv(sig,frame):
    IOLoop.current().stop()

def main():
    from tornado.log import enable_pretty_logging
    enable_pretty_logging()
    setupDb()
    initIpaddr()
    app = make_app()
    app.listen(8888)
    signal.signal(signal.SIGINT,stop_serv)
    IOLoop.current().start()

if __name__ == '__main__':
    main()