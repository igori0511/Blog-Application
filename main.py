#include user libraries
import sys
sys.path.insert(0, 'libs')
# very important
import os
import jinja2
from validate import validation
from hashes import *
from databases import *
import webapp2
import json
import logging
import time
#import memcache
#cache system
from google.appengine.api import memcache

#get current directory
template_dir = os.path.join(os.getcwd(),'templates')
#initialize template engine
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

#cache the front page
#set the time between quries
timeKey = "time"
memcache.set(timeKey,time.time())

# cache front page
def cache_front(update = False):
    key = "top"
 
    #will convert python data type into string
    #then convert it back to the python data type
    blog = memcache.get(key)

    if blog is None or update:
        logging.error("DB QUERY")
        #get blog entries
        blog = db.GqlQuery("SELECT * FROM Blog "
                           "ORDER By created DESC")

        blog = list(blog)
        memcache.set(key,blog)
        memcache.set(timeKey,time.time())

    return blog


#handle template processing using jinja2 templates
class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)
        
    def render_str(self,template,**params):
        t=jinja_env.get_template(template)
        return t.render(params)
    
    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))

    def user_id(self,user):
        return str(user.key().id())
        
    def set_cookie(self,user):
        #get user id
        id = self.user_id(user)
        #make a new cookie
        new_cookie_val = Hash.make_secure_val(id)
        #set cookie
        self.response.headers.add_header('Set-Cookie', 'user_id=%s;Path=/' % new_cookie_val)
            

#registration handler
class RegisterHandler(Handler):

    #render html page
    def render_page(self,**values):
        self.render("registration.html",**values)
        
    #get method  - browser request    
    def get(self):
        self.render_page()
   

    #post method - server responce    
    def post(self):
        #assume that the information is valid
        valid = True
        values = dict({})        
        #get uset information
        #get username from the form
        username      = self.request.get("username")
        #get password from the form
        password      = self.request.get("password")
        #get password one more time from the form
        verify        = self.request.get("verify")
        #get email if user provides it from the form
        email         = self.request.get("email")
        
        #check if username is valid
        valid_user_name     = validation.valid_username(username)
        #check if password is valid
        valid_password      = validation.valid_password(password)
        #check if email is valid 
        valid_verify_email  = validation.valid_email(email)
        
        # if username is not valid init first error
        if not valid_user_name:
            values["error1"] = "That's not a valid username."
            valid = False
        #check if the user already registered    
        if user_accounts.by_name(username):
            values["error1"] = "Username already exist!"
            valid = False
            
        # if password not valid
        #init second error    
        if not valid_password:
            values["error2"] = "Thats not a valid password"
            valid = False
        
        # if passwords don't match
        #init error 3    
        if password != verify:
            values["error3"] = "Password don't match."
            valid = False
        # if email isn't valid and email not empty
        # init error4    
        if not valid_verify_email and email != "":
            values["error4"] = "Thats not a valid email adress."
            valid = False
        #if input isn't valid write corresponding errors    
        if not valid:
            #add username and email to dict
            values["username"] = username
            values["email"]    = email
            #render our page
            self.render_page(**values)
        #else add data to the database
        else :
            #create an instance of a database
            user = user_accounts(username = username,
                                 password=Hash.make_pw_hash(username,password),
                                 email=email)
            #put that data in the database
            user.put()
            #set cookie, supply the id of the entity
            self.set_cookie(user)            
            # redirect
            self.redirect("/blog/welcome")

#login class
class Login(Handler):
        # renders our page
    def render_page(self,**error):
        self.render("login.html",**error)
    
        # get method(getting data from the server)
    def get(self):
            self.render_page()
    # check if the entered info is valid
    def check_user(self,name,pw,user):
            # if value not none
        if user:
                #check the user return true if pw and name are correct false otherwise
                return Hash.valid_pw(name,pw,user.password)
        else:
            # if empty return False    
                return False
    
    def post(self):
            #request username       
        username = self.request.get("username")
            #request password        
        password = self.request.get("password")

            #get user info from the database
        user  = user_accounts.by_name(username)
        #check if supplied information is valid     
        if self.check_user(username,password,user):
                self.set_cookie(user)
                self.redirect("/blog/welcome")
            # else rerender form with a error    
        else:
                self.render_page(login_error = "Invalid login")

#logout class
class Logout(Handler):
    
        #logout from the system
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect("/blog/signup")
            
#redirection   

class Welcome(Handler):
    #get method (to get data from the server)
    def get(self):
        #get cookie from the browser
        cookie_str = self.request.cookies.get('user_id')
        #check if cookie is valid
        cookie_val = Hash.check_secure_val(cookie_str)
        #if it is not valid 
        if not cookie_val:
            #redirect to a signup page
            self.redirect("/blog/signup")
        else:
            # render form    
            user = user_accounts.by_id(int(cookie_val))
            self.render("welcome.html", user = user.username)
###################################################################
#
#permalink handler
class PermalinkHandler(Handler):
    
    def get(self, blog_id):
        key = "POST_" + str(blog_id)

        post = memcache.get(key)

        curTime = time.time()
        if post is None:
            logging.error("DB QUERY")

            post = (Blog.get_by_id(int(blog_id)),curTime)
            memcache.set(key,(post[0],curTime))

        ourTime = curTime - post[1]    

        self.render("frontpage.html", blogs = [post[0]],renderTime = "Queried " + str(int(ourTime))+ " seconds ago")

#main handler that handles main page(where blog entries occur)
class MainHandler(Handler):
    #render database
    def render_page(self):
        datastore = cache_front()
        ourTime = time.time() - memcache.get("time")
        self.render("frontpage.html",blogs = datastore,renderTime = "Queried " + str(int(ourTime))+ " seconds ago")

    #get data from server
    def get(self):
        self.render_page()    

                
#newposthandler handles adding new posts
class NewPostHandler(Handler):
    def render_page(self, subject="",content="",error=""):
        self.render("newpost.html",subject = subject,content=content,error=error) 

    def get(self):
        self.render_page()

    def wipe_data(self):
        q = db.GqlQuery("SELECT * FROM Blog")
        results = q.fetch(10)
        db.delete(results)
 
    def post(self):
        #get subject
        subject = self.request.get("subject")
        #get content    
        content = self.request.get("content")
        #check if input is valid
        if content and subject:
            #create a new art property
            b = Blog(subject = subject, content = content)
            #store instance of blog
            b.put()
            time.sleep(0.5)
            cache_front(True)

            #redirect to permalink
            self.redirect("/blog/%d" % b.key().id())
        else:
            error = "subject and content required!"
            self.render_page(subject=subject,content=content,error=error)

class JsonHandler(Handler):
    #generate json for whole blog
    def jsonBlog(self):
        #get all data from the database
        cursor = Blog.get_data()
        json_list = []    
        #generate json
        for entry in cursor:
            json_list.append({"content":entry.content,"subject":entry.subject})
        #dump json
        self.write(json.dumps(json_list))
        
    #generate json only for one entry
    def jsonEntry(self,blog_id):
        cursor = Blog.get_by_id(int(blog_id))
        #create json
        json_dict = {"content":cursor.content,"subject":cursor.subject}
        #dump json
        self.write(json.dumps(json_dict))

    #main get method
    def get(self,blog_id = None):
        #set content type
        self.response.headers['Content-Type'] = "application/json"
        #generate json for the whole blog
        if not blog_id:
            
            self.jsonBlog()
        else:
            self.jsonEntry(blog_id)

class MemFlush(Handler):

    def get(self):
        memcache.flush_all()
        self.redirect("/blog")

                
#initialize app
app = webapp2.WSGIApplication([
    ('/blog/?', MainHandler),
    ('/blog/newpost',NewPostHandler),
    ('/blog/(\d+)',PermalinkHandler),
    ('/blog/signup', RegisterHandler),
    ('/blog/welcome',Welcome),
    ('/blog/login',  Login),
    ('/blog/logout', Logout),
    ('/blog/.json',JsonHandler),
    ('/blog/(\d+).json',JsonHandler),
    ('/blog/flush/?',MemFlush)
], debug=True)
