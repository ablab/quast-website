import os
import sys

import logging
logger = logging.getLogger('quast')

from django.conf import settings
from django import forms
from django.forms import fields, widgets
if not settings.QUAST_DIRPATH in sys.path:
    sys.path.insert(1, settings.QUAST_DIRPATH)
from quast_libs import qconfig

from models import User, UserSession, DataSet, ContigsFile, QuastSession


class DataSetForm(forms.Form):
    def __init__(self, us, *args, **kwargs):
        super(DataSetForm, self).__init__(*args, **kwargs)

        self.fields['name_selected'].choices = [('', '')] + \
            [(d.name, d.name) for d in us.get_all_allowed_dataset_set()
                .filter(remember=True)
                .extra(select={'lower_name': 'lower(name)'})
                .order_by('lower_name')]

        # if qs:
        #     self.initial = {
        #         'report_id': qs.report_id,
        #         'name_selected': qs.data_set.name if qs.data_set else None,
        #         'min_contig': qs.min_contig,
        #         'scaffolds': qs.scaffolds,
        #         'domain': qs.eukaryotic,
        #         'estimated_ref_size': qs.estimated_ref_size,
        #         'find_genes': qs.find_genes,
        #     }

    contigs = fields.CharField(validators=[], widget=forms.Textarea)

    report_id = fields.CharField(required=True, widget=widgets.TextInput)

    min_contig = fields.IntegerField(
        min_value=0,
        required=False,
        widget=widgets.TextInput(attrs={'tabindex': '2'}))

    scaffolds = fields.BooleanField(
        required=False,
        widget=widgets.CheckboxInput(attrs={'tabindex': '3'}),
        label='Scaffolds <span style="color: #888;">(adds assemblies splitted by fragments of N\'s &ge; 10 bp)</span>')

    find_genes = fields.BooleanField(
        required=False,
        label='Find genes <span style="color: #888;">(GlimmerHMM)</span>',
        widget=widgets.CheckboxInput(attrs={'tabindex': '4'}),
        help_text='Takes time')

    domain = fields.ChoiceField(
        required=True,
        choices=[(False, 'Prokaryotic <span style="color: #888;">(process circular chromosomes)</span>'),
                 (True, 'Eukaryotic')],
        widget=widgets.RadioSelect(attrs={'tabindex': '5'}))

    estimated_ref_size = fields.IntegerField(
        min_value=0,
        required=False,
        widget=widgets.TextInput(attrs={'tabindex': ''}))

    # min_contig = fields.IntegerField(min_value=0, required=False, initial=0,
    #                                  widget=widgets.TextInput(attrs={'tabindex': '2'}))
    #
    # scaffolds = fields.BooleanField(required=False, initial=False,
    #                                 widget=widgets.CheckboxInput(attrs={'tabindex': '3'}),
    #                                 label='Scaffolds',
    #                                 help_text='Adds split assemblies (continuous fragments of N\'s longer than 10 bp.)')
    #
    # domain = fields.ChoiceField(required=True,
    #                             choices=((False, 'Prokaryotic <span class="comment_to_field">(find genes with GenemarkS, process circular chromosomes)</span>'),
    #                                      (True, 'Eukaryotic <span class="comment_to_field">(find genes with GlimmerHMM)</span>')), initial=False,
    #                             widget=widgets.RadioSelect(attrs={'tabindex': '4'}))
    #                             # help_text='Useful for gene finding (the domains have different gene features, '
    #                             #           'so we use GenemarkS for prokaryotes and GlimmerHMM for eukaryotes) '
    #                             #           'and for contig analyzing (to&nbsp;deal with prokaryotic circular chromosomes).')
    #                                       # <br><span style="margin-left: -3px;">(</span>
    # estimated_ref_size = fields.IntegerField(min_value=0, required=False, initial=0,
    #                                          widget=widgets.TextInput(attrs={'tabindex': ''}))
    #
    # find_genes = fields.BooleanField(required=False, initial=False,
    #                                  widget=widgets.CheckboxInput(attrs={'tabindex': ''}),
    #                                  help_text='Takes time')

    name_selected = fields.ChoiceField(
        required=False,
        widget=widgets.Select(attrs={
            'class': 'chzn-select-deselect',
            'data-placeholder': 'unknown genome',
            'tabindex': '6',
        }))

    is_created = fields.BooleanField(initial=False,
                                     required=False,
                                     widget=widgets.CheckboxInput(attrs={'tabindex': '7',
                                                                         'class': 'dotted-link'}))

    name_created = fields.CharField(required=False,
                                    widget=widgets.TextInput(attrs={'tabindex': '8'}),
                                    help_text='If you fill&nbsp;in this field, we will remember the data set using this name.')

    reference = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex': '9'}),
                                 help_text='FASTA file with the reference genome sequence.')

    genes = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex': '10'}),
                             help_text='See <a href="http://cab.cc.spbu.ru/quast/manual.html#sec2.2">manual</a> for file formats.')

    operons = fields.FileField(required=False, widget=widgets.FileInput(attrs={'tabindex': '11'}),
                               help_text='See <a href="http://cab.cc.spbu.ru/quast/manual.html#sec2.2">manual</a> for file formats.')

    caption = fields.CharField(required=False, widget=widgets.TextInput(attrs={'tabindex': '12', 'style': 'width: 302px;'}))

    # initial = {'created_or_selected': 'selected'}

    # def set_report_id(self, report_id):
    #     self.fields['report_id'] = fields.CharField(
    #         required=True,
    #         initial=report_id,
    #         widget=widgets.TextInput)

    # def set_email(self, email):
    #     self.fields['email'] = fields.EmailField(
    #         required=False,
    #         initial=email,
    #         widget=widgets.TextInput(attrs={'tabindex': '10', 'style': 'width: 302px;'})
    #     )

    # def set_default_data_set_name(self, data_set_name):
    #     self.fields['name_selected'].initial = data_set_name

    # @staticmethod
    # def create_from_qs(qs):
    #     form = DataSetForm(qs.us, initial={
    #         'report_id': qs.report_id,
    #         'name_selected': qs.data_set.name if qs.data_set else None,
    #         'min_contig': qs.min_contig,
    #         'scaffolds': qs.scaffolds,
    #         'domain': qs.eukaryotic,
    #         'estimated_ref_size': qs.estimated_ref_size,
    #         'find_genes': qs.find_genes,
    #     })

        # form.fields['name_selected'] = fields.ChoiceField(
        #     required=False,
        #     initial=qs.data_set.name if qs.data_set else None,
        #     choices=[('', '')] + [(d.name, d.name) for d in qs.user_session.get_all_allowed_dataset_set()
        #         .filter(remember=True)
        #         .extra(select={'lower_name': 'lower(name)'})
        #         .order_by('lower_name')],
        #     widget=widgets.Select(attrs={
        #         'class': 'chzn-select-deselect',
        #         'data-placeholder': 'unknown genome',
        #         'tabindex': '3',
        #     }))
        #
        # form.fields['min_contig'] = fields.IntegerField(
        #     min_value=0, required=False, initial=qs.min_contig,
        #     widget=widgets.TextInput(attrs={'tabindex': '2'}))
        #
        # form.fields['scaffolds'] = fields.BooleanField(
        #     required=False,
        #     initial=qs.scaffolds,
        #     widget=widgets.CheckboxInput(attrs={'tabindex': '3'}),
        #     label='Scaffolds',
        #     help_text='Adds split assemblies (continuous fragments of N\'s longer than 10 bp.)')
        #
        # form.fields['domain'] = fields.ChoiceField(
        #     required=True,
        #     choices=[(False, 'Prokaryotic <span style="color: #888;">(<span class="find_genes_notion">find genes with GenemarkS, </span>process circular chromosomes)</span>'),
        #              (True, 'Eukaryotic<span class="find_genes_notion"> <span style="color: #888;">(find genes with GlimmerHMM)</span></span>')],
        #     initial=qs.eukaryotic,
        #     widget=widgets.RadioSelect(attrs={'tabindex': '4'}))
        #
        # form.fields['estimated_ref_size'] = fields.IntegerField(
        #     min_value=0,
        #     required=False,
        #     initial=qs.estimated_ref_size,
        #     widget=widgets.TextInput(attrs={'tabindex': ''}))
        #
        # form.fields['find_genes'] = fields.BooleanField(
        #     required=False,
        #     initial=qs.find_genes,
        #     widget=widgets.CheckboxInput(attrs={'tabindex': ''}),
        #     help_text='Takes time')

        # return form

    def clean(self):  # Validation
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