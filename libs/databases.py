#import databasemodel
from google.appengine.ext import db

#create user_acount database
class user_accounts(db.Model):
        #create column username in database
        username = db.StringProperty(required = True)
        #create column with hashed password
        password = db.StringProperty(required = True)
        #create column for an email
        email    = db.StringProperty()
        
        @classmethod
        def by_id(self,uid):
            u = user_accounts.get_by_id(uid)
            return u

        @classmethod
        def wipe_data(self):
            q = db.GqlQuery("SELECT * FROM user_accounts")
            results = q.fetch(1000)
            db.delete(results) 

        @classmethod
        def get_data(self):
            query = db.GqlQuery("SELECT * FROM user_accounts")
            return query
        
        @classmethod
        def by_name(cls,name):
            u = user_accounts.all().filter('username =', name).get()
            return u   
                

                
#make a database for storing users content
class Blog(db.Model):
    #create column subject in data base
    subject = db.StringProperty(required = True)
    #create column blog
    content = db.TextProperty(required = True)
    #auto_now_add = auto create time and date
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def get_data(self):
            cursor = db.GqlQuery("SELECT * FROM Blog")
            return cursor
  
