import os
import sys

from django.conf import settings
from django.forms import forms, fields, widgets
if not settings.QUAST_DIRPATH in sys.path:
    sys.path.insert(1, settings.QUAST_DIRPATH)
from libs import qconfig

from models import Dataset, ContigsFile, UserSession, QuastSession


class DatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DatasetForm, self).__init__(*args, **kwargs)
        self.fields['name_selected'] = fields.ChoiceField(
            required=False,
            choices=[(d.name, d.name) for d in Dataset.objects.all()
                     if d.remember] + [('no data set', 'no data set')],
            widget=widgets.Select(attrs={
                'class': 'chzn-select',
                'data-placeholder': 'Select data set...'
            })
        )

    created_or_selected = fields.CharField(initial='selected')

    name_selected = fields.ChoiceField(
        required=False,
        #        choices=[(d.name, d.name) for d in Dataset.objects.all()],
        widget=widgets.Select(attrs={
            'class': 'chzn-select',
            'data-placeholder': 'Select data set...'
        })
    )

    name_created = fields.CharField(required=False, widget=widgets.TextInput())

    min_contig = fields.IntegerField(min_value=0, required=False, initial=0)

    reference = fields.FileField(required=False)
    genes = fields.FileField(required=False)
    operons = fields.FileField(required=False)

    initial={
        'created_or_selected': 'selected'
    }

    def set_min_contig(self, min_contig):
        self.fields['min_contig'] = fields.IntegerField(
            min_value=0,
            required=False,
            initial=min_contig
        )

    def set_user_session(self, user_session):
        self.user_session = user_session

    def clean(self):
        cleaned_data = super(DatasetForm, self).clean()

        if self.user_session:
            if not self.user_session.contigsfile_set or\
               not self.user_session.contigsfile_set.all().exists():
                raise forms.ValidationError('No contigs provided')

        return cleaned_data


class UserForm(forms.Form):
    email = fields.EmailField(required=True)


class AdminDatasetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AdminDatasetForm, self).__init__(*args, **kwargs)
        self.fields['reference_fname'].required = False

    class Meta:
        model = Dataset


from django.contrib import admin

class UserSessionAdmin(admin.ModelAdmin):
    pass

class DatasetAdmin(admin.ModelAdmin):
#    form = AdminDatasetForm
    pass

class ContigsFileAdmin(admin.ModelAdmin):
    pass

class QuastSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(ContigsFile, ContigsFileAdmin)
admin.site.register(Dataset, DatasetAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(QuastSession, QuastSessionAdmin)