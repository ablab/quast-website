# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'QuastSession.min_contig'
        db.delete_column('quast_app_quastsession', 'min_contig')

        # Adding field 'QuastSession.link'
        db.add_column('quast_app_quastsession', 'link',
                      self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True),
                      keep_default=False)


        # Changing field 'QuastSession.report_id'
        db.alter_column('quast_app_quastsession', 'report_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256))
        # Removing index on 'QuastSession', fields ['report_id']
        db.delete_index('quast_app_quastsession', ['report_id'])


        # Changing field 'Dataset.dirname'
        db.alter_column('quast_app_dataset', 'dirname', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from='name', unique_with=()))

    def backwards(self, orm):
        # Adding index on 'QuastSession', fields ['report_id']
        db.create_index('quast_app_quastsession', ['report_id'])

        # Adding field 'QuastSession.min_contig'
        db.add_column('quast_app_quastsession', 'min_contig',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'QuastSession.link'
        db.delete_column('quast_app_quastsession', 'link')


        # Changing field 'QuastSession.report_id'
        db.alter_column('quast_app_quastsession', 'report_id', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

        # Changing field 'Dataset.dirname'
        db.alter_column('quast_app_dataset', 'dirname', self.gf('autoslug.fields.AutoSlugField')(max_length=50, unique_with=(), unique=True, populate_from=None))

    models = {
        'quast_app.contigsfile': {
            'Meta': {'object_name': 'ContigsFile'},
            'file_index': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['quast_app.UserSession']", 'null': 'True', 'blank': 'True'})
        },
        'quast_app.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'dirname': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': "'name'", 'unique_with': '()'}),
            'genes_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'operons_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'reference_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'remember': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'quast_app.quastsession': {
            'Meta': {'object_name': 'QuastSession'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '200000', 'null': 'True', 'blank': 'True'}),
            'contigs_files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['quast_app.ContigsFile']", 'through': "orm['quast_app.QuastSession_ContigsFile']", 'symmetrical': 'False'}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.Dataset']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'report_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'submited': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.UserSession']"})
        },
        'quast_app.quastsession_contigsfile': {
            'Meta': {'object_name': 'QuastSession_ContigsFile'},
            'contigs_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.ContigsFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quast_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.QuastSession']"})
        },
        'quast_app.usersession': {
            'Meta': {'object_name': 'UserSession'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['quast_app']