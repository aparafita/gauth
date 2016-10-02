#Gauth (Google-Auth)

Easy connector to Google APIs.

Create an authorization instance (Gauth):
* Use gauth.authorize(scope, client_id, client_secret, email, filename, browser=True)
    * scope is a unique string or a list of strings with the scopes to authorize
    * client_id, client_secret: strings; can be obtained from Google API Console
    * email: email of the user that gives authorization to their resources
    * filename: filename where to store the Gauth instance
    * browser: whether to open the browser directly or just print the url in the console

* The result of this function is the gauth instance, which will be saved automatically

Load an authorization instance:
* Use gauth.load(filename)

Use an authorization instance:
* Given a Gauth instance already created/loaded, call the methods .get, .post, .put, .delete, .patch
just as one would normally use the 'requests' library functions. Gauth will automatically authorize 
all requests done with this methods