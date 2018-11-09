from app import db

class User(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True)
	archivedDocuments = db.relationship('Document', 
							backref=db.backref('archiveUser',
								lazy='joined', 
								uselist = False),
							lazy='dynamic')

	def __repr__(self):
		return '<User %r>' % (self.name)


class Document(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True)
	description = db.Column(db.Text)
	date = db.Column(db.DateTime)
	filePath = db.Column(db.String(260))
	fileExtension = db.Column(db.String(10))
	archivedOn =  db.Column(db.DateTime)
	archivedBy = db.Column(db.Integer, db.ForeignKey('user.id_'))
	storageId = db.Column(db.Integer, db.ForeignKey('storage.id_'))
	tags = db.relationship('Tag', secondary='document_tag_link', lazy='dynamic')
	storage = db.relationship('Storage', lazy='joined')
		
	def __repr__(self):
		return '<Document %r>' % (self.name)


class Storage(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	boxId = db.Column(db.Integer)
	slotId = db.Column(db.Integer)
	archivedDocument = db.relationship('Document', 
							backref=db.backref('physicalStorage', 
								lazy='joined', 
								uselist = False),
							lazy='joined',
							uselist = False)

	def __repr__(self):
		return '<Storage: box=%r, slot=%r>' % (self.boxId, self.slotId)


class Tag(db.Model):
	id_ = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), index=True, unique=True)
	docs = db.relationship('Document', secondary='document_tag_link', lazy='dynamic')
		

def getAllTags():
	tags = Tag.query.all()
	result = []
	for t in tags:
		result.append(t.name)
	return result

class Document_Tag_Link(db.Model):	
	__tablename__ = 'document_tag_link'
	tag_id = db.Column('tag_id', db.Integer, db.ForeignKey('tag.id_'), primary_key=True)
	document_id = db.Column(db.Integer, db.ForeignKey('document.id_'), primary_key=True)
	tag = db.relationship(Tag, backref=db.backref('Tag'))
	document = db.relationship(Document, backref=db.backref('Document'))

def getDocumentsWithNameMatching(criteria):
	docs = Document.query.filter(Document.name.contains(criteria)).all()
	return docs

def getDocumentsWithTagMatching(criteria):
	tags = Tag.query.filter(Tag.name == criteria).all()
	result = []
	for t in tags:
		for d in t.docs:
			result.append(d)
	return result
