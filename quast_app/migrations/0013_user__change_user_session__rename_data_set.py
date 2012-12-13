# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('quast_app_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('input_dirname', self.gf('django.db.models.fields.CharField')(unique=True, max_length=256)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True)),
        ))
        db.send_create_signal('quast_app', ['User'])

        # Renaming field 'QuastSession.dataset' to 'QuastSession.data_set'
        db.rename_column('quast_app_quastsession', 'dataset_id', 'data_set_id')

        # Renaming field 'QuastSession.submited' to 'QuastSession.submitted'
        db.rename_column('quast_app_quastsession', 'submited', 'submitted')

        # Adding field 'QuastSession.user'
        db.add_column('quast_app_quastsession', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'QuastSession.min_contig'
        db.add_column('quast_app_quastsession', 'min_contig',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'QuastSession.user_session'
        db.alter_column('quast_app_quastsession', 'user_session_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.UserSession'], null=True))

        # Deleting field 'UserSession.is_authorized'
        db.delete_column('quast_app_usersession', 'is_authorized')

        # Deleting field 'UserSession.password'
        db.delete_column('quast_app_usersession', 'password')

        # Deleting field 'UserSession.email'
        db.delete_column('quast_app_usersession', 'email')

        # Adding field 'UserSession.user'
        db.add_column('quast_app_usersession', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['quast_app.User'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table('quast_app_user')

        # Renaming field 'QuastSession.data_set' to 'QuastSession.dataset'
        db.rename_column('quast_app_quastsession', 'data_set_id', 'dataset_id')

        # Renaming field 'QuastSession.submitted' to 'QuastSession.submited'
        db.rename_column('quast_app_quastsession', 'submitted', 'submited')

        # Deleting field 'QuastSession.user'
        db.delete_column('quast_app_quastsession', 'user_id')

        # Deleting field 'QuastSession.min_contig'
        db.delete_column('quast_app_quastsession', 'min_contig')


        # Changing field 'QuastSession.user_session'
        db.alter_column('quast_app_quastsession', 'user_session_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['quast_app.UserSession']))
        # Adding field 'UserSession.is_authorized'
        db.add_column('quast_app_usersession', 'is_authorized',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserSession.password'
        db.add_column('quast_app_usersession', 'password',
                      self.gf('django.db.models.fields.CharField')(max_length=256, null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserSession.email'
        db.add_column('quast_app_usersession', 'email',
                      self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True),
                      keep_default=False)

        # Deleting field 'UserSession.user'
        db.delete_column('quast_app_usersession', 'user_id')


    models = {
        'quast_app.contigsfile': {
            'Meta': {'object_name': 'ContigsFile'},
            'file_index': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.UserSession']", 'null': 'True', 'blank': 'True'})
        },
        'quast_app.dataset': {
            'Meta': {'object_name': 'DataSet'},
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
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.DataSet']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'min_contig': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'report_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'submitted': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.User']", 'null': 'True', 'blank': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.UserSession']", 'null': 'True', 'blank': 'True'})
        },
        'quast_app.quastsession_contigsfile': {
            'Meta': {'object_name': 'QuastSession_ContigsFile'},
            'contigs_file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.ContigsFile']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quast_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.QuastSession']"})
        },
        'quast_app.user': {
            'Meta': {'object_name': 'User'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'})
        },
        'quast_app.usersession': {
            'Meta': {'object_name': 'UserSession'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'session_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['quast_app']