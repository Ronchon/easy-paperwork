#Model
class Page:
	def __init__(self, url, view, blueprint):
		self.url = url
		self.view = view
		self.blueprint = blueprint
		self.fullview = blueprint + '.' + view

#Instances
Login = Page('/login', 'login', 'users')
Password = Page('/password', 'password', 'users')
Home = Page('/home', 'home', 'documents')
