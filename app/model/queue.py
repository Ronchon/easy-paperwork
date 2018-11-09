import os
import uuid
import operator
from datetime import datetime
from app import database, db
from app.database import Tag, Document, Document_Tag_Link, Storage

htmlMimeTypes = {
	'pdf': 'application/pdf', 
	'png': 'image/png',
	'jpg': 'image/jpeg',
	'FOLDER': 'Unknown'
	}

class QueueManager(object):
	
	def __init__(self, path):
		self.path = path
		self.refresh()
	
	def refresh(self):
		self.documents = {}
		for file_ in os.listdir(str(self.path)):
			doc = DocToArchive(str(file_), self.path)
			self.documents[doc.id_] = doc
			
	def getDocumentsByName(self):
		return sorted(self.documents.values(), 
					key=operator.attrgetter('name'))


class DocToArchive(object):
	
	def __init__(self, fullName, path):
		self.id_ = str(uuid.uuid4())
		self.fullName = fullName
		self.path = path
		self.findNameAndType(fullName)
		self.fullPath = self.path + '/' + fullName
		self.destinationPath = ''
		self.tags = ''
		self.description = ''
		self.month = ''
		self.year = ''
		self.date = datetime.now()
		self.box = ''
		self.slot = ''
		self.relevance = 1
		self.tags = ''
	
	def findNameAndType(self, fullName):
		index = fullName.find('.')
		if index>-1:
			self.name = fullName[:index]
			self.type_ = fullName[index+1:]
		else:
			self.name = fullName
			self.type_ = 'FOLDER'

	def getHtmlMimeType(self):
		return htmlMimeTypes[self.type_]


class ArchiveManager(object):
	
	def __init__(self, path):
		self.path = path
		self.permanentPath = path + 'Permanent'
		self.byDatePath = path + 'ByDate' 
	
	def getFolderByDate(self, docDate):
		directoryPath = self.byDatePath + '/' + docDate.strftime('%Y') + docDate.strftime('%m')
		if not os.path.exists(directoryPath):
			os.makedirs(directoryPath)
		return directoryPath
		
	def getFolderPermanent(self):
		directoryPath = self.permanentPath
		if not os.path.exists(directoryPath):
			os.makedirs(directoryPath)
		return directoryPath
	
	def generateId(self):
		return str(uuid.uuid4())
	
	def saveInDatabase(self, docToSave):
		existingTags = database.getAllTags()
		docTags =  docToSave.tags.upper().split(',')
		d = Document(name=docToSave.name)
		d.description=docToSave.description
		d.date=docToSave.date
		d.filePath = docToSave.path + '/' 
		d.fileExtension = '.' + docToSave.type_
		d.archivedOn = datetime.now()
		for docTag in docTags:
			t = Tag(name= docTag)
			if str(docTag) in existingTags:
				t= Tag.query.filter_by(name=str(docTag)).first()
			db.session.add(t)
			dt = Document_Tag_Link(tag = t , document = d)
			db.session.add(dt)
		if docToSave.box != 0:
			s = Storage(boxId=docToSave.box, slotId=docToSave.slot,archivedDocument = d)
			db.session.add(s)
		db.session.add(d)	
		db.session.commit()
		return d.id_
	
	def processDocument(docName, docDescription, docDate, docTags, isPermanent):
		return True
	


class SearchEngine(object):
	
	def __init__(self):
		self.criteria = []
		self.nameRelevance = 10
		self.tagRelevance = 4
	
	def splitCriteria(self, textCriteria):
		self.criteria = textCriteria.upper().split(' ')
	
	def reset(self):
		self.criteria = []
	
	def returnResults(self):
		self.documents = {}
		if len(self.criteria) > 0:
			docs = []
			for c in self.criteria:
				docs = database.getDocumentsWithNameMatching(c)
				for doc in docs:
					if doc.id_ in self.documents:
						self.documents[doc.id_].relevance = self.documents[doc.id_].relevance*self.nameRelevance
					else:
						d = DocToArchive(str(doc.id_) + doc.fileExtension, doc.filePath)
						d.name = doc.name
						d.description = doc.description
						d.month = doc.date.month
						d.year = doc.date.year
						if doc.storage:
							d.box = doc.storage.boxId
							d.slot = doc.storage.slotId
						else:
							d.box = 0
							d.slot = 0
						d.id_ = doc.id_
						for t in doc.tags:
							if d.tags == '':
								d.tags += t.name
							else:
								d.tags += ',' + t.name 
						d.relevance = self.nameRelevance
						self.documents[d.id_]=d
				docs = database.getDocumentsWithTagMatching(c)
				for doc in docs:
					if doc.id_ in self.documents:
						self.documents[doc.id_].relevance = self.documents[doc.id_].relevance*self.tagRelevance
					else:
						d = DocToArchive(str(doc.id_) + doc.fileExtension, doc.filePath)
						d.name = doc.name
						d.description = doc.description
						d.month = doc.date.month
						d.year = doc.date.year
						if doc.storage:
							d.box = doc.storage.boxId
							d.slot = doc.storage.slotId
						else:
							d.box = 0
							d.slot = 0
						d.id_ = doc.id_
						for t in doc.tags:
							if d.tags == '':
								d.tags += t.name
							else:
								d.tags += ',' + t.name 
						d.relevance = self.tagRelevance
						self.documents[d.id_]= d
		return sorted(self.documents.values(), 
					key=operator.attrgetter('relevance'), reverse=True)
	
	def modifyInDatabase(self, docToEdit):
		docTags =  docToEdit.tags.upper().split(',')
		d = Document.query.filter_by(id_=int(docToEdit.id_)).first()
		d.name = docToEdit.name
		d.description=docToEdit.description
		d.date=docToEdit.date
		for oldT in d.tags:
			queryOldLink = Document_Tag_Link.query.filter_by(tag_id = oldT.id_, document_id = d.id_ )
			if len(queryOldLink.all()) != 0:
				dtOld = queryOldLink.first()
				if not oldT.name in docTags:
					db.session.delete(dtOld)
		for docTag in docTags:
			queryTag = Tag.query.filter_by(name=str(docTag))
			if len(queryTag.all()) == 0:
				t = Tag(name= docTag)
				dt = Document_Tag_Link(tag = t , document = d)
			else:
				t = queryTag.first()
				queryDocLink = Document_Tag_Link.query.filter_by(tag_id = t.id_, document_id = d.id_ )
				if len(queryDocLink.all()) == 0:
					dt = Document_Tag_Link(tag = t , document = d)
				else:
					dt = queryDocLink.first()
			db.session.add(t)
			db.session.add(dt)
		if docToEdit.box != 0:
			queryStorage = Storage.query.filter_by(boxId=docToEdit.box, slotId=docToEdit.slot)
			if len(queryStorage.all()) == 0:
				s = Storage(boxId=docToEdit.box, slotId=docToEdit.slot,archivedDocument = d)
			else:
				s = queryStorage.first()
				s.archivedDocument = d
			db.session.add(s)
		db.session.add(d)	
		db.session.commit()
		return d.id_
