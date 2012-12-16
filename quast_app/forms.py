import os
import sys

import logging
logger = logging.getLogger('quast')

from django.conf import settings
from django.forms import forms, fields, widgets
if not settings.QUAST_DIRPATH in sys.path:
    sys.path.insert(1, settings.QUAST_DIRPATH)
from libs import qconfig

from models import User, UserSession, DataSet, ContigsFile, QuastSession


class DataSetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DataSetForm, self).__init__(*args, **kwargs)
        self.fields['name_selected'] = fields.ChoiceField(
            required=False,
            choices=self.__get_choices(),
            widget=widgets.Select(attrs={
                'class': 'chzn-select-deselect',
                'data-placeholder': 'unknown genome',
                'tabindex': '3',
            })
        )

    def __get_choices(self):
        return [('', '')] + [(d.name, d.name) for d in DataSet.objects.all() if d.remember]

    is_created = fields.BooleanField(initial=False, required=False)
    name_created = fields.CharField(required=False,
                                    widget=widgets.TextInput(attrs={'tabindex':'5'}))

    contigs = fields.CharField(widget=forms.Textarea, validators=[])
    report_id = fields.CharField(required=True, widget=widgets.TextInput)
    min_contig = fields.IntegerField(min_value=0, required=False, initial=0, widget=widgets.TextInput(attrs={'tabindex':'2'}))

    reference = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'6'}))
    genes = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'7'}))
    operons = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex':'8'}))

    caption = fields.CharField(required=False, widget=widgets.TextInput(attrs={'tabindex':'9', 'style': 'width: 302px;'}))
    comment = fields.CharField(required=False, widget=widgets.Textarea(attrs={'tabindex':'10', 'rows': '2', 'style': 'width: 302px;'}))
    # email = fields.EmailField(required=False, widget=widgets.TextInput(attrs={'tabindex':'11', 'style': 'width: 302px;'}))

    initial = {
        'created_or_selected': 'selected'
    }

    def set_report_id(self, report_id):
        self.fields['report_id'] = fields.CharField(
            required=True,
            widget=widgets.TextInput
        )

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

    def set_default_data_set_name(self, data_set_name):
        self.fields['name_selected'].initial = data_set_name

    def clean(self):    # Validation
        cleaned_data = super(DataSetForm, self).clean()

        # if self.user_session:
        #     if not self.user_session.contigsfile_set or\
        #        not self.user_session.contigsfile_set.all().exists():
        #         raise forms.ValidationError('No contigs provided')

        return cleaned_data


class AdminDataSetForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AdminDataSetForm, self).__init__(*args, **kwargs)
        self.fields['reference_fname'].required = False

    class Meta:
        model = DataSet


from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    pass

class UserSessionAdmin(admin.ModelAdmin):
    pass

class DataSetAdmin(admin.ModelAdmin):
    pass

class ContigsFileAdmin(admin.ModelAdmin):
    pass

class QuastSessionAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(ContigsFile, ContigsFileAdmin)
admin.site.register(QuastSession, QuastSessionAdmin)