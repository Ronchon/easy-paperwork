from flask import render_template, flash, redirect, request, url_for, session, send_file
from app import app, database
from .model.forms import QueueForm, ArchiveForm, SearchForm, EditForm
from .model.queue import QueueManager, ArchiveManager, DocToArchive, SearchEngine
from datetime import datetime
import os

QUEUE_PATH = app.config['QUEUE_FOLDER']
ARCHIVE_PATH = app.config['ARCHIVE_FOLDER']
QUEUE_MANAGER = QueueManager(QUEUE_PATH)
ARCHIVE_MANAGER = ArchiveManager(ARCHIVE_PATH) #TODO: is uppercase a good practice here??
SEARCH_ENGINE = SearchEngine()

@app.route('/')
@app.route('/index')
def index():
	hardcodedUser = { 'firstName': 'Audrey' } 	#hardcoded user
	session['username'] = hardcodedUser.get('firstName') #TODO:handle sessioninformation elsewhere (controller)
	flash(session['username']) #TODO: remove useless flash
	flash(session.sid) #TODO: handle session timeout
	return render_template('index.html', 
							title='Home', 
							user=hardcodedUser)
							
@app.route('/queue', methods=['GET', 'POST'])
def queue():
	form = QueueForm()
	if form.validate_on_submit():
		if form.refresh.data:
			QUEUE_MANAGER.refresh()
		elif form.archive.data:
			selection = request.form.getlist('selection')
			if len(selection) != 1:
				flash('Please select 1 file (only!) to archive')
			else:
				return redirect('/archive/' + selection[0])
	return render_template('queue.html', 
							title='Documents in queue',
							form=form,
							documents=QUEUE_MANAGER.getDocumentsByName())

@app.route('/search', methods=['GET', 'POST'])
def search():
	form = SearchForm()
	if form.cancel.data:
		SEARCH_ENGINE.reset()
		return redirect(url_for('index'))
	if form.validate_on_submit():
		if form.search.data:
			SEARCH_ENGINE.splitCriteria(form.criteria.data)
		elif form.edit.data:
			selection = request.form.getlist('selection')
			if len(selection) != 1:
				flash('Please select 1 file (only!) to edit')
			else:
				return redirect('/edit/' + selection[0])
	return render_template('search.html', 
							title='Search Documents',
							form=form,
							documents=SEARCH_ENGINE.returnResults())

@app.route('/archive/<documentId>', methods=['POST'])
def submitArchive(documentId):
	form = ArchiveForm()
	if form.cancel.data:
		return redirect(url_for('queue'))
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
			return redirect(url_for('queue'))
	return render_template('archive.html', 
				title='Archive',
				form=form,
				doc=QUEUE_MANAGER.documents[documentId])
				
@app.route('/archive/<documentId>', methods=['GET'])
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

@app.route('/preview/<previewId>')
def preview(previewId):	
	if previewId in QUEUE_MANAGER.documents:
		return send_file(session['previewPath'])

@app.route('/previewEdit/<previewId>')
def previewEdit(previewId):	
	if int(previewId) in SEARCH_ENGINE.documents:
		return send_file(session['previewPath'])
#TODO: model should manage data, logic, rules
#TODO: controller does the conversion between model and views

@app.route('/edit/<documentId>', methods=['POST'])
def submitEdit(documentId):
	form = EditForm()
	docToEdit = DocToArchive(form.name.data,'')
	if form.cancel.data:
		return redirect(url_for('search'))
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
			return redirect(url_for('search'))
	return render_template('edit.html', 
				title='Edit',
				form=form,
				doc=docToEdit)

@app.route('/edit/<documentId>', methods=['GET'])
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
