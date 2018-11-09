from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField
from wtforms import SelectField, SelectMultipleField
from datetime import datetime

class QueueForm(FlaskForm):
	refresh = SubmitField(label='Refresh')
	archive = SubmitField(label='Archive Selection')
	
class ArchiveForm(FlaskForm):
	name = StringField(label='Name')
	description = TextAreaField(label='Description')
	documentYear = IntegerField(label='Year document', default=datetime.now().year)
	documentMonth = IntegerField(label='Month document', default=datetime.now().month)
	documentTags = TextAreaField(label='Tags')
	isPermanent = BooleanField(label='IsPermanent')
	boxNumber = IntegerField(label='Box document', default=0)
	slotNumber = IntegerField(label='Slot document', default=0)
	cancel = SubmitField(label='Cancel')
	submit = SubmitField(label='Submit')

	def isArchivePossible(self):
		return name and documentMonth and documentYear and documentTags
	
class SearchForm(FlaskForm):
	criteria = StringField(label='Criteria')
	documentYear = IntegerField(label='Year document')
	documentMonth = IntegerField(label='Month document')
	isPermanent = BooleanField(label='IsPermanent')	
	search = SubmitField(label='Search')
	cancel = SubmitField(label='Cancel')
	edit = SubmitField(label='Edit')

class EditForm(FlaskForm):
	name = StringField(label='Name')
	description = TextAreaField(label='Description')
	documentYear = IntegerField(label='Year document', default=datetime.now().year)
	documentMonth = IntegerField(label='Month document', default=datetime.now().month)
	documentTags = TextAreaField(label='Tags')
	boxNumber = IntegerField(label='Box document', default=0)
	slotNumber = IntegerField(label='Slot document', default=0)
	cancel = SubmitField(label='Cancel')
	submit = SubmitField(label='Submit')

	def isEditPossible(self):
		return name and documentMonth and documentYear and documentTags
