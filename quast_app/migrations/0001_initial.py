# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserSession'
        db.create_table('quast_app_usersession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('input_dirname', self.gf('django.db.models.fields.CharField')(max_length=2048)),
        ))
        db.send_create_signal('quast_app', ['UserSession'])

        # Adding model 'Dataset'
        db.create_table('quast_app_dataset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('remember', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('reference_fname', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('genes_fname', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('operons_fname', self.gf('django.db.models.fields.CharField')(max_length=2048, null=True, blank=True)),
            ('dirname', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=None, unique_with=())),
        ))
        db.send_create_signal('quast_app', ['Dataset'])

        # Adding model 'ContigsFile'
        db.create_table('quast_app_contigsfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fname', self.gf('django.db.models.fields.CharField')(max_length=2048)),
            ('user_session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.UserSession'])),
            ('file_index', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal('quast_app', ['ContigsFile'])

        # Adding model 'QuastSession'
        db.create_table('quast_app_quastsession', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.UserSession'])),
            ('dataset', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.Dataset'], null=True)),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=1024, null=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('report_id', self.gf('autoslug.fields.AutoSlugField')(unique=True, max_length=50, populate_from=None, unique_with=())),
        ))
        db.send_create_signal('quast_app', ['QuastSession'])

        # Adding model 'QuastSession_ContigsFile'
        db.create_table('quast_app_quastsession_contigsfile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('quast_session', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.QuastSession'])),
            ('contigs_file', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.ContigsFile'])),
        ))
        db.send_create_signal('quast_app', ['QuastSession_ContigsFile'])


    def backwards(self, orm):
        # Deleting model 'UserSession'
        db.delete_table('quast_app_usersession')

        # Deleting model 'Dataset'
        db.delete_table('quast_app_dataset')

        # Deleting model 'ContigsFile'
        db.delete_table('quast_app_contigsfile')

        # Deleting model 'QuastSession'
        db.delete_table('quast_app_quastsession')

        # Deleting model 'QuastSession_ContigsFile'
        db.delete_table('quast_app_quastsession_contigsfile')


    models = {
        'quast_app.contigsfile': {
            'Meta': {'object_name': 'ContigsFile'},
            'file_index': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.UserSession']"})
        },
        'quast_app.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'dirname': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'genes_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'operons_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'reference_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'remember': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'quast_app.quastsession': {
            'Meta': {'object_name': 'QuastSession'},
            'contigs_files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['quast_app.ContigsFile']", 'through': "orm['quast_app.QuastSession_ContigsFile']", 'symmetrical': 'False'}),
            'dataset': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.Dataset']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'report_id': ('autoslug.fields.AutoSlugField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None', 'unique_with': '()'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['quast_app']