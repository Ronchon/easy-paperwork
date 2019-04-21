from flask import render_template, flash, redirect, request, url_for, session, send_file, Blueprint
from app import app, database
from .model.forms import QueueForm, ArchiveForm, SearchForm, EditForm
from .model.queue import QueueManager, ArchiveManager, DocToArchive, SearchEngine
from datetime import datetime
import os


#Blueprint for users
#users_bp = Blueprint('users', __name__, template_folder='templates')

#Login route 
#users_bp.add_url_rule(
#	directory.Login.url, 
#	view_func=LoginView.as_view(directory.Login.view))

#Password route
#users_bp.add_url_rule(
#	directory.Password.url, 
#	view_func=PasswordView.as_view(directory.Password.view))

#Blueprint for documents
documents_bp = Blueprint('documents', __name__, template_folder='templates')

QUEUE_PATH = app.config['QUEUE_FOLDER']
ARCHIVE_PATH = app.config['ARCHIVE_FOLDER']
QUEUE_MANAGER = QueueManager(QUEUE_PATH)
ARCHIVE_MANAGER = ArchiveManager(ARCHIVE_PATH) #TODO: is uppercase a good practice here??
SEARCH_ENGINE = SearchEngine()

@documents_bp.route('/')
@documents_bp.route('/home')
def home():
	hardcodedUser = { 'firstName': 'Audrey' } 	#hardcoded user
	session['username'] = hardcodedUser.get('firstName') #TODO:handle sessioninformation elsewhere (controller)
	flash(session['username']) #TODO: remove useless flash
	flash(session.sid) #TODO: handle session timeout
	return render_template('home.html', 
							title='Home', 
							user=hardcodedUser)
							
@documents_bp.route('/queue', methods=['GET', 'POST'])
def queue():
	form = QueueForm()
	if form.validate_on_submit():
		if form.refresh.data:
			QUEUE_MANAGER.refresh()
		elif form.archive.data:
			if QUEUE_MANAGER.selectedId != "":
				return redirect('/archive/' + QUEUE_MANAGER.selectedId)
	return render_template('queue.html', 
							title='Documents in queue',
							form=form,
							documents=QUEUE_MANAGER.getDocumentsByName())
							
@documents_bp.route('/queue/select_document', methods=['POST'])
def selectDocumentFromQueue():
	QUEUE_MANAGER.selectedId = request.form.get('selectedId')
	return redirect(url_for('documents.queue'))

@documents_bp.route('/search', methods=['GET', 'POST'])
def search():
	form = SearchForm()
	if form.cancel.data:
		SEARCH_ENGINE.reset()
		return redirect(url_for('documents.home'))
	if form.validate_on_submit():
		if form.search.data:
			SEARCH_ENGINE.splitCriteria(form.criteria.data)
		elif form.edit.data:
			if SEARCH_ENGINE.selectedId != "":
				return redirect('/edit/' + SEARCH_ENGINE.selectedId)
	return render_template('search.html', 
							title='Search Documents',
							form=form,
							documents=SEARCH_ENGINE.returnResults())

@documents_bp.route('/search/select_document', methods=['POST'])
def selectDocumentFromSearch():
	SEARCH_ENGINE.selectedId = request.form.get('selectedId')
	return redirect(url_for('documents.search'))

@documents_bp.route('/archive/<documentId>', methods=['POST'])
def submitArchive(documentId):
	form = ArchiveForm()
	if form.cancel.data:
		QUEUE_MANAGER.refresh()
		return redirect(url_for('documents.queue'))
	if form.validate_on_submit():
		if form.isArchivePossible:				
			formDocument = DocToArchive(QUEUE_MANAGER.documents[documentId].fullName, '')
			formDocument.name = form.name.data
			formDocument.description = form.description.data
			formDocument.date = datetime(year=form.documentYear.data, month=form.documentMonth.data, day=1)				
			if form.isPermanent.data:
				formDocument.path = ARCHIVE_MANAGER.getFolderPermanent()
			else:
				formDocument.path = ARCHIVE_MANAGER.getFolderByDate(formDocument.date)
			formDocument.tags = form.documentTags.data
			formDocument.box = form.boxNumber.data
			formDocument.slot = form.slotNumber.data
			session['currentbox'] = form.boxNumber.data
			session['currentslot'] = form.slotNumber.data
			formDocument.id_ = ARCHIVE_MANAGER.saveInDatabase(formDocument)
			os.rename(QUEUE_MANAGER.documents[documentId].fullPath, (formDocument.path + '/' + str(formDocument.id_) + '.' + formDocument.type_))
			flash('Archivage ' + formDocument.name )
			QUEUE_MANAGER.refresh()
			return redirect(url_for('documents.queue'))
	return render_template('archive.html', 
				title='Archive',
				form=form,
				doc=QUEUE_MANAGER.documents[documentId])
				
@documents_bp.route('/archive/<documentId>', methods=['GET'])
def archive(documentId):
	#Initialize Form
	form = ArchiveForm()
	if 'currentbox' in session and 'currentslot' in session:
		form.boxNumber.data = session['currentbox']
		form.slotNumber.data = session['currentslot']
	if documentId in QUEUE_MANAGER.documents:
		session['previewPath'] = QUEUE_MANAGER.documents[documentId].fullPath
	else:
		session['previewPath'] = ''
	return render_template('archive.html', 
				title='Archive',
				form=form,
				doc=QUEUE_MANAGER.documents[documentId])

@documents_bp.route('/preview/<previewId>')
def preview(previewId):	
	if previewId in QUEUE_MANAGER.documents:
		return send_file(session['previewPath'])

@documents_bp.route('/previewEdit/<previewId>')
def previewEdit(previewId):	
	if int(previewId) in SEARCH_ENGINE.documents:
		return send_file(session['previewPath'])
#TODO: model should manage data, logic, rules
#TODO: controller does the conversion between model and views

@documents_bp.route('/edit/<documentId>', methods=['POST'])
def submitEdit(documentId):
	form = EditForm()
	docToEdit = DocToArchive(form.name.data,'')
	if form.cancel.data:
		SEARCH_ENGINE.reset()
		return redirect(url_for('documents.search'))
	if form.validate_on_submit():
		if form.isEditPossible and form.submit.data:
			docToEdit.id_ = documentId 
			docToEdit.name = form.name.data
			docToEdit.description = form.description.data
			docToEdit.date = datetime(year=form.documentYear.data, month=form.documentMonth.data, day=1)
			docToEdit.tags = form.documentTags.data
			docToEdit.box = form.boxNumber.data
			docToEdit.slot = form.slotNumber.data
			SEARCH_ENGINE.modifyInDatabase(docToEdit)
			flash('Edit ' + docToEdit.name )
			SEARCH_ENGINE.returnResults()
			return redirect(url_for('documents.search'))
	return render_template('edit.html', 
				title='Edit',
				form=form,
				doc=docToEdit)

@documents_bp.route('/edit/<documentId>', methods=['GET'])
def edit(documentId):
	form = EditForm()
	docToEdit = SEARCH_ENGINE.documents[int(documentId)]
	docToEdit.id_= str(docToEdit.id_)
	form.name.data = docToEdit.name
	form.description.data = docToEdit.description
	form.documentMonth.data = docToEdit.month
	form.documentYear.data = docToEdit.year
	form.boxNumber.data = docToEdit.box
	form.slotNumber.data = docToEdit.slot
	form.documentTags.data = docToEdit.tags
	session['previewPath'] = str(docToEdit.fullPath)
	return render_template('edit.html', 
				title='Edit',
				form=form,
				doc=docToEdit)