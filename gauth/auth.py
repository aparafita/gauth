# Author: Álvaro Parafita (parafita.alvaro@gmail.com)

"""
    Module responsible for the creation of an object 
    that stores and refreshes access tokens.
"""

import os.path

import requests
import json
import webbrowser

from .decorators import retry


def auth_dec(func):
    """
        Decorator that ensures that a requests method
        accepts an 'auth' object that contains the access_token
        needed to authorize the request. 
        It also refreshes the token when it is expired.
    """

    def authorize(auth, kwargs):
        # Temporal function that adds access_token to headers
        headers = kwargs.get('headers', {})
        headers['Authorization'] = 'Bearer ' + auth.access_token

        kwargs['headers'] = headers # in case it didn't exist


    from functools import wraps

    @wraps(func)
    def f(*args, **kwargs):
        auth = kwargs.pop('gauth') if 'gauth' in kwargs else None

        if auth:
            authorize(auth, kwargs) # changes kwargs

        r = func(*args, **kwargs)

        if auth and r.status_code == 401:
            # Access token expired
            auth.refresh()
            authorize(auth, kwargs) # changes kwargs

            return func(*args, **kwargs) # reexecute with refreshed auth

        else:
            return r

    # Decorate f with retry: avoid RequestExceptions
    f = retry(requests.exceptions.RequestException, times=2)(f)

    return f


class Gauth(object):

    authorization_url = 'https://accounts.google.com/o/oauth2/auth'
    token_url = 'https://www.googleapis.com/oauth2/v3/token'
    redirect_url = 'urn:ietf:wg:oauth:2.0:oob'


    def __init__(
        self, client_id, client_secret, 
        scopes, email, filename,
        access_token, refresh_token
    ):
        """ 
            Constructor of the class Gauth.

            client_id - client id used to make the call
            client_secret - client secred used to use the client id
            scopes - list of scopes authorized in this instance
            email - email of the user authorizing
            filename - location of the file where to save the instance
            access_token - token used to make the calls
            refresh_token - token used to refresh the access_token when expired
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.email = email
        self.filename = filename
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.save()


    @staticmethod
    def authorize(scopes, client_id, client_secret, email, filename, browser=True):
        """ 
            Creates an Auth instance with all the necessary data
            to authorize requests in name of the specified email,
            given the scopes of credentials to use (a single string or a list of strings), 
            and the client_id - client_secret 
            for the client that will be authorized.

            - scopes: list of scopes to authorize.
            - client_id, client_secret: client credentials to use. 
            - email: email of the user to get the authorization.
            - filename: filename where to store the auth data.
            - browser: boolean, defaults to True. 
                Determines whether to open the browser automatically 
                during the auth process or to print the URL.
        """

        if type(scopes) == str:
            scopes = [scopes]

        # Ask for the authorization url
        auth_response = requests.get(
            Gauth.authorization_url, 
            params={
                'client_id': client_id, 
                'response_type': 'code',
                'redirect_uri': Gauth.redirect_url,
                'scope': ' '.join(scopes),
                'login_hint': email
            }
        )

        # Raise an Exception if status_code not OK
        auth_response.raise_for_status()

        if browser:
            # Open url where the user will authorize the scopes
            webbrowser.open(auth_response.url)
        else:
            print('Open the following url: ' + auth_response.url)

        authorization_code = input('Enter the resulting authorization code: ')

        # Ask for the token
        token_response = requests.post(
            Gauth.token_url,
            params={
                'code': authorization_code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': Gauth.redirect_url,
                'grant_type': 'authorization_code'
            }
        )

        # Raise an Exception if status_code not OK
        token_response.raise_for_status() 

        token_json = token_response.json()

        return Gauth(
            client_id, client_secret, scopes, email, filename, 
            token_json['access_token'], token_json['refresh_token']
        )


    @retry(requests.exceptions.RequestException, times=2)
    def _request(self, method, *args, **kwargs):
        """
            Function that performs the HTTP method ensuring 
            sending the proper access_token 
            and refreshing it automatically if it expired.
        """

        def authorize(kwargs):
            # Temporal function that adds access_token to headers
            headers = kwargs.get('headers', {})
            headers['Authorization'] = 'Bearer ' + self.access_token

            kwargs['headers'] = headers # in case it didn't exist

        authorize(kwargs)
        r = method(*args, **kwargs)

        if r.status_code == 401:
            # Access token expired
            self.refresh()
            authorize(kwargs) # changes kwargs

            return method(*args, **kwargs) # reexecute with refreshed auth

        else:
            return r


    def get(self, *args, **kwargs):
        return self._request(requests.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request(requests.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request(requests.put, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request(requests.delete, *args, **kwargs)

    def patch(self, *args, **kwargs):
        return self._request(requests.patch, *args, **kwargs)
            

    def refresh(self):
        """ Refreshes the access_token of this instance """

        refresh_response = requests.post(
            Gauth.token_url,
            params={
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token'
            }
        )

        # Raise an Exception if status_code not OK
        refresh_response.raise_for_status()

        self.access_token = refresh_response.json()['access_token']

        self.save()


    def save(self):
        """
            Saves the Auth dict to its JSON file
        """

        d = {
            name: getattr(self, name)
            
            for name in [
                'client_id', 
                'client_secret', 
                'scopes', 
                'email',
                'filename',
                'access_token', 
                'refresh_token'
            ]
        }

        with open(self.filename, 'w') as f:
            f.write(json.dumps(d, indent=2))


    @staticmethod
    def load(filename):
        """ 
            Loads an Auth instance given a filename
        """
    
        with open(filename) as f:
            j = json.loads(f.read())
        
        return Gauth(
            j['client_id'], j['client_secret'], 
            j['scopes'], j['email'], filename, 
            j['access_token'], j['refresh_token']
        )


load = Gauth.load # make it accessible through the module
authorize = Gauth.authorize