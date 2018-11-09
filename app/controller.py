from flask import render_template, flash, redirect, request, url_for, session, send_file
from app import app
from .forms import QueueForm, ArchiveForm
from .model.queue import QueueManager

#NOT USED
# Do we need a controller???


PATH = app.config['QUEUE_FOLDER']
QUEUE_MANAGER = QueueManager(PATH)


@app.route('/')
@app.route('/index')
def index():
	hardcodedUser = { 'firstName': 'Audrey' } 	#hardcoded user
	session['username'] = hardcodedUser.get('firstName') #TODO:handle sessioninformation elsewhere (controller)
	flash(session['username']) #TODO: remove useless flash
	flash(session.sid)
	return render_template('index.html', 
							title='Home', 
							user=hardcodedUser)
							
@app.route('/queue', methods=['GET', 'POST'])
def queue():
	form = QueueForm()
	files = QUEUE_MANAGER.files
	
	if form.validate_on_submit():
		if form.refresh.data:
			flash('Refresh requested')
			QUEUE_MANAGER.refresh()
		elif form.archive.data:
			flash('Archive requested')
			selection = request.form.getlist('selection')
			if len(selection) != 1:
				flash('Please select 1 file (only!) to archive')
			else:
				selectionText = files[int(selection[0])].get('name')
				return redirect(url_for('archive', archive=int(selection[0])))
		return render_template('queue.html', 
							title='Files in queue',
							form=form,
							files=files)
	return render_template('queue.html', 
							title='Files in queue',
							form=form,
							files=files)
							
@app.route('/archive', methods=['GET', 'POST'])
def archive():
	form = ArchiveForm()
	selectedFile = QUEUE_MANAGER.files[int(request.args.get('archive'))]
	session['previewType'] = selectedFile.get('type')
	session['previewPath'] = selectedFile.get('fullPath')
	mimeTypesDic = {'pdf': 'application/pdf', 'png': 'image/png'} #TODO: move in a static variable file
	if form.validate_on_submit():
		if form.cancel.data:
			return redirect(url_for('index'))
	return render_template('archive.html', 
							title='Archive',
							form=form,
							file=selectedFile,
							previewId = session.sid + str(selectedFile.get('id')) + '.' + session['previewType'],
							previewType = mimeTypesDic[session['previewType']])
							
@app.route('/preview/<previewId>')
def preview(previewId):	
	if previewId.startswith(session.sid):
		return send_file(session['previewPath'])
		
#TODO: model should manage data, logic, rules
#TODO: controller does the conversion between model and views
