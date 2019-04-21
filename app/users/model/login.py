#----------imports----------#
from flask import flash, redirect, render_template, request, url_for
from flask.views import MethodView

import json
import requests
from werkzeug.security import check_password_hash

from app import directory
from app.users.model import login_constants as lc
from app.users.model.forms import LoginForm, PasswordForm


#----------View Classes----------#
class LoginView(MethodView):

    def __init__(self):
        self.template = 'login.html'
        self.form = LoginForm()
        self.title = 'Login'

    def get(self):
        if LoginHandler().validateGoogleCode(request):
            LoginHandler().retrieveUserProfile(request)
            flash(LoginHandler().userDisplayName)
            return redirect(url_for(directory.Password.fullview))
        return render_template(
            self.template,
            form=self.form,
            title=self.title)

    def post(self):
        if self.form.validate_on_submit():
            return redirect(lc.GoogleParams.authorize_url)
        return render_template(
            self.template,
            form=self.form,
            title=self.title)

class PasswordView(MethodView):

    def __init__(self):
        self.template = 'login.html'
        self.form = PasswordForm()
        self.title = 'Password'

    def get(self):
        return render_template(
            self.template,
            form=self.form,
            title=self.title)

    def post(self):
        if self.form.validate_on_submit():
            if LoginHandler().checkPassword(str(self.form.password.data)):
                return redirect(url_for(directory.Home.fullview))
        return render_template(
            self.template,
            form=self.form,
            title=self.title)


#----------Handler Classes----------#
class LoginHandler(object):

    class __LoginHandler:

        def __init__(self):
            # TODO : should have a link to session object?
            self.accessToken = ''
            self.userDisplayName = ''

        def validateGoogleCode(self, request):
            if request.args.get(lc.GoogleParams.code):
                _code = request.args.get(lc.GoogleParams.code)
                _post = requests.post(
                                    lc.GoogleParams.token_uri,
                                    data=lc.GoogleParams.requestParameters(_code))
                _response = json.loads(_post.text)
                self.accessToken = _response[lc.GoogleParams.access_token]
                return True
            return False

        def retrieveUserProfile(self, request):
            _params = {lc.GoogleParams.key: lc.GoogleParams.client_id,
                          lc.GoogleParams.access_token: self.accessToken}
            _get = requests.get(lc.GoogleParams.profile_api_url, params=_params)
            _response = json.loads(_get.text)
            self.userDisplayName = _response[lc.GoogleParams.display_name]

        def checkPassword(self, password):
            return check_password_hash(lc.Hash, password)

    instance = None

    def __new__(cls):
        if not LoginHandler.instance:
            LoginHandler.instance = LoginHandler.__LoginHandler()
        return LoginHandler.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)
