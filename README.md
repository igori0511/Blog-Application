###This is a basic blog application on Google App Engine
####Supports basic functionality of a blog this includes:
1. Adding new posts
2. Registration
3. Loggin
4. API - return's whole blog as JSON and the individual posts

####Supports Memcached for the fron page and the initial posts


###List of handlers:
1.    ('/blog/?', MainHandler),
2.    ('/blog/newpost',NewPostHandler),
3.    ('/blog/(\d+)',PermalinkHandler),
4.    ('/blog/signup', RegisterHandler),
5.    ('/blog/welcome',Welcome),
6.    ('/blog/login',  Login),
7.    ('/blog/logout', Logout),
8.    ('/blog/.json',JsonHandler),
9.    ('/blog/(\d+).json',JsonHandler),
10.   ('/blog/flush/?',MemFlush)



###Download google app engine for Python 2.7 from:
https://developers.google.com/appengine/downloads

###To start the app locally:
1. Add the app to your project list in GAE launcher and click the run button
2. Go to your browser of choice and type: **localhost:*port/blog***

###Other links:
1. **localhost:*port/blog/***
2. **localhost:*port/blog/newpost***
3. **localhost:*port/blog/postID***
4. **localhost:*port/blog/signup***
5. **localhost:*port/blog/welcome***
6. **localhost:*port/blog/login***
7. **localhost:*port/blog/logout***
8. **localhost:*port/blog/.json***
9. **localhost:*port/blog/postID.json***
10. **localhost:*port/blog/flush/optional(can be an id of the individual post)***


###To Deploy the application to Google do the following:
1. Add the app to your project list in GAE launcher
2. Login to your google email
3. Go to https://appengine.google.com/start and create an application
4. Modify the *app.yaml* file as follows:
	change the the top most line ***application: blogapplication1992***
	to ***application: Application Identifier***
5. Finaly In GAE launcher select the project and click *Deploy*


###Working project:
[Working blog application](http://blogapplication1992.appspot.com/blog)
