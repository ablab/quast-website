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
                'data-placeholder': 'Select data set...',
                'tabindex': '3',
            })
        )

#    created_or_selected = fields.CharField(initial='selected')
    is_created = fields.BooleanField(initial=False, required=False)

    name_selected = fields.ChoiceField(
        required=False,
        #        choices=[(d.name, d.name) for d in Dataset.objects.all()],
        widget=widgets.Select(attrs={
            'class': 'chzn-select',
            'data-placeholder': 'Select data set...'
        })
    )

    name_created = fields.CharField(required=False,
                                    widget=widgets.TextInput(attrs={'tabindex':'5'}))

    min_contig = fields.IntegerField(min_value=0, required=False, initial=0, widget=widgets.TextInput(attrs={'tabindex':'2'}))

    reference = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'6'}))
    genes = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'7'}))
    operons = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'8'}))

    caption = fields.CharField(required=False, widget=widgets.TextInput(attrs={'tabindex':'9', 'style': 'width: 302px;'}))
    comment = fields.CharField(required=False, widget=widgets.Textarea(attrs={'tabindex':'10', 'rows': '2', 'style': 'width: 302px;'}))
    email = fields.EmailField(required=False, widget=widgets.TextInput(attrs={'tabindex':'11', 'style': 'width: 302px;'}))

    initial = {
        'created_or_selected': 'selected'
    }

    def set_min_contig(self, min_contig):
        self.fields['min_contig'] = fields.IntegerField(
            min_value=0,
            required=False,
            initial=min_contig,
            widget=widgets.TextInput(attrs={'tabindex':'2'})
        )

    def set_user_session(self, user_session):
        self.user_session = user_session

    def set_email(self, email):
        self.fields['email'] = fields.EmailField(
            required=False,
            initial=email,
            widget=widgets.TextInput(attrs={'tabindex':'10', 'style': 'width: 302px;'})
        )

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