#Model
class GoogleParameters:
    def __init__(self):
        #TODO split between fields, urls and other information
        self.display_name = 'displayName'
        self.access_token = 'access_token'
        self.key = 'key'
        self.code = 'code'
        self.auth_uri = "https://accounts.google.com/o/oauth2/auth"
        self.redirect_uri = "http://localhost:5000/login"
        self.token_uri = "https://www.googleapis.com/oauth2/v4/token"
        self.client_id = "827049491387-gsppqr9t9pj6701h0tcb49vc09p4g" \
                         "n9k.apps.googleusercontent.com"
        self.client_secret = "wyIC4NhW71K9A2xm8vs3r0Qv"
        self.scope = "https://www.googleapis.com/auth/userinfo.profile"
        self.authorize_url = self.auth_uri \
                            + "?redirect_uri=" + self.redirect_uri \
                            + "&prompt=consent&response_type=code" \
                            + "&client_id=" + self.client_id \
                            + "&scope=" + self.scope \
                            + "&access_type=offline"
        self.profile_api_url = 'https://www.googleapis.com/plus/v1/people/me'

    def requestParameters(self, code):
        return dict(
                code=code,
                redirect_uri=self.redirect_uri,
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type="authorization_code")

#Instances
GoogleParams = GoogleParameters()
Hash = "pbkdf2:sha256:50000$XcEPxGsZ$65753ebe942979a8be77caf2f10988b" \
        "e05f3616381a754ea499ac3501f1682e9"
  