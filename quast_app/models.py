#from django.db import models
#from django.forms import ModelForm
#
#class Session(models.Model):
#    session_key = models.CharField(max_length=100)
#
#
#
#class Dataset(models.Model):
#    name = models.CharField(max_length=1000)
#    selected = True
#    reference_file = models.FileField()
#    genes_file = models.FileField()
#    operons_file = models.FileField()
#
#
#class DatasetForm(ModelForm):
#    class Meta:
#        model = Dataset



from autoslug.fields import AutoSlugField
from django.db import models

class UserSession(models.Model):
    session_key = models.CharField(max_length=256)
    input_dirname = models.FilePathField()


class Dataset(models.Model):
    name = models.CharField(max_length=1024)
    reference_fname = models.FilePathField(null=True)
    genes_fname = models.FilePathField(null=True)
    operons_fname = models.FilePathField(null=True)

    dirname = AutoSlugField(populate_from='name', unique=True)
    def __unicode__(self):
        return self.name


class ContigsFileName(models.Model):
    fname = models.FilePathField()
    user_session = models.ForeignKey('UserSession')
#    quast_session = models.ForeignKey('QuastSession', null=True)


class QuastSession(models.Model):
    user_session = models.ForeignKey(UserSession)
    dataset = models.ForeignKey(Dataset)
    task_id = models.CharField(max_length=1024, null=True)
    contigs_filenames = models.ManyToManyField(ContigsFileName, through='QuastSession_ContigsFileName')

    date = models.DateTimeField(auto_now_add=True)
    report_id = AutoSlugField(populate_from='date', unique=True)

    def get_results_reldirpath(self):
        return self.user_session.session_key + '/' + self.date.strftime('%Y-%m-%d_%H-%M-%S-%f')


class QuastSession_ContigsFileName(models.Model):
    quast_session = models.ForeignKey(QuastSession)
    contigs_filename = models.ForeignKey(ContigsFileName)



from django.forms import forms, fields, widgets

class DatasetForm(forms.Form):
    created_or_selected = fields.CharField(initial='selected')

    name_selected = fields.ChoiceField(
        required=False,
        choices=[(d.name, d.name) for d in Dataset.objects.all()],
        widget=widgets.Select(attrs={'class': 'chzn-select',
                                     'data-placeholder': 'Select dataset...'})
    )

    name_created = fields.CharField(required=False,
        widget=widgets.TextInput(attrs={'id': 'dataset-name-add-input'}))
    reference = fields.FileField(required=False)
    genes = fields.FileField(required=False)
    operons = fields.FileField(required=False)

    initial={'created_or_selected': 'selected'}

