
from autoslug.fields import AutoSlugField
from django.db import models

class UserSession(models.Model):
    session_key = models.CharField(max_length=256)
    input_dirname = models.FilePathField()


class Dataset(models.Model):
    name = models.CharField(max_length=1024)
    remember = models.BooleanField()

    reference_fname = models.FilePathField(null=True)
    genes_fname = models.FilePathField(null=True)
    operons_fname = models.FilePathField(null=True)

    dirname = AutoSlugField(populate_from='name', unique=True)
    def __unicode__(self):
        return self.name


class ContigsFile(models.Model):
    fname = models.FilePathField()
    user_session = models.ForeignKey('UserSession')
    file_index = models.CharField(max_length=256)
#   quast_session = models.ForeignKey('QuastSession', null=True)


class QuastSession(models.Model):
    user_session = models.ForeignKey(UserSession)
    dataset = models.ForeignKey(Dataset, null=True)
    task_id = models.CharField(max_length=1024, null=True)
    contigs_files = models.ManyToManyField(ContigsFile, through='QuastSession_ContigsFile')

    date = models.DateTimeField()

    report_id = AutoSlugField(populate_from=(lambda instance: instance.date.strftime('%d_%b_%Y_%H:%M:%S.%f')),
                              unique=True,
                              slugify=(lambda s: s))

    def get_results_reldirpath(self):
        return self.user_session.session_key + '/' + self.report_id.__str__()


class QuastSession_ContigsFile(models.Model):
    quast_session = models.ForeignKey(QuastSession)
    contigs_file = models.ForeignKey(ContigsFile)



from django.forms import forms, fields, widgets

class DatasetForm(forms.Form):
    created_or_selected = fields.CharField(initial='selected')

    name_selected = fields.ChoiceField(
        required=False,
#        choices=[(d.name, d.name) for d in Dataset.objects.all()],
        widget=widgets.Select(attrs={
            'class': 'chzn-select',
            'data-placeholder': 'Select dataset...'
        })
    )

    name_created = fields.CharField(required=False, widget=widgets.TextInput())
    reference = fields.FileField(required=False)
    genes = fields.FileField(required=False)
    operons = fields.FileField(required=False)

    initial={'created_or_selected': 'selected'}

    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['name_selected'] = fields.ChoiceField(
            required=False,
            choices=[(d.name, d.name) for d in Dataset.objects.all() if d.remember] + [('no dataset', 'no dataset')],
            widget=widgets.Select(attrs={
                'class': 'chzn-select',
                'data-placeholder': 'Select dataset...'
            })
        )

    def set_user_session(self, user_session):
        self.user_session = user_session

    def clean(self):
        cleaned_data = super(DatasetForm, self).clean()

        if self.user_session:
            if not self.user_session.contigsfile_set or \
               not self.user_session.contigsfile_set.all().exists():
                raise forms.ValidationError('No contigs provided')

        return cleaned_data


from django.contrib import admin
class UserSessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(UserSession, UserSessionAdmin)


class DatasetAdmin(admin.ModelAdmin):
    pass
admin.site.register(Dataset, DatasetAdmin)


class ContigsFileAdmin(admin.ModelAdmin):
    pass
admin.site.register(ContigsFile, ContigsFileAdmin)


class QuastSessionAdmin(admin.ModelAdmin):
    pass
admin.site.register(QuastSession, QuastSessionAdmin)