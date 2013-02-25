# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'UserSession.min_contig'
        db.add_column('quast_app_usersession', 'min_contig',
                      self.gf('django.db.models.fields.IntegerField')(default=500),
                      keep_default=False)

        # Adding field 'UserSession.scaffolds'
        db.add_column('quast_app_usersession', 'scaffolds',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserSession.eukaryotic'
        db.add_column('quast_app_usersession', 'eukaryotic',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'UserSession.estimated_ref_size'
        db.add_column('quast_app_usersession', 'estimated_ref_size',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'UserSession.find_genes'
        db.add_column('quast_app_usersession', 'find_genes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'User.min_contig'
        db.add_column('quast_app_user', 'min_contig',
                      self.gf('django.db.models.fields.IntegerField')(default=500),
                      keep_default=False)

        # Adding field 'User.scaffolds'
        db.add_column('quast_app_user', 'scaffolds',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'User.eukaryotic'
        db.add_column('quast_app_user', 'eukaryotic',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'User.estimated_ref_size'
        db.add_column('quast_app_user', 'estimated_ref_size',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'User.find_genes'
        db.add_column('quast_app_user', 'find_genes',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'QuastSession.scaffoldic'
        db.delete_column('quast_app_quastsession', 'scaffoldic')

        # Adding field 'QuastSession.scaffolds'
        db.add_column('quast_app_quastsession', 'scaffolds',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'UserSession.min_contig'
        db.delete_column('quast_app_usersession', 'min_contig')

        # Deleting field 'UserSession.scaffolds'
        db.delete_column('quast_app_usersession', 'scaffolds')

        # Deleting field 'UserSession.eukaryotic'
        db.delete_column('quast_app_usersession', 'eukaryotic')

        # Deleting field 'UserSession.estimated_ref_size'
        db.delete_column('quast_app_usersession', 'estimated_ref_size')

        # Deleting field 'UserSession.find_genes'
        db.delete_column('quast_app_usersession', 'find_genes')

        # Deleting field 'User.min_contig'
        db.delete_column('quast_app_user', 'min_contig')

        # Deleting field 'User.scaffolds'
        db.delete_column('quast_app_user', 'scaffolds')

        # Deleting field 'User.eukaryotic'
        db.delete_column('quast_app_user', 'eukaryotic')

        # Deleting field 'User.estimated_ref_size'
        db.delete_column('quast_app_user', 'estimated_ref_size')

        # Deleting field 'User.find_genes'
        db.delete_column('quast_app_user', 'find_genes')

        # Adding field 'QuastSession.scaffoldic'
        db.add_column('quast_app_quastsession', 'scaffoldic',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'QuastSession.scaffolds'
        db.delete_column('quast_app_quastsession', 'scaffolds')


    models = {
        'quast_app.contigsfile': {
            'Meta': {'object_name': 'ContigsFile'},
            'file_index': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'fname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'quast_app.dataset': {
            'Meta': {'object_name': 'DataSet'},
            'dirname': ('autoslug.fields.AutoSlugField', [], {'unique_with': '()', 'max_length': '50', 'populate_from': "'name'"}),
            'genes_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'operons_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'reference_fname': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'remember': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.User']", 'null': 'True', 'blank': 'True'}),
            'user_session': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.UserSession']", 'null': 'True', 'blank': 'True'})
        },
        'quast_app.quastsession': {
            'Meta': {'object_name': 'QuastSession'},
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '200000', 'null': 'True', 'blank': 'True'}),
            'contigs_files': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['quast_app.ContigsFile']", 'through': "orm['quast_app.QuastSession_ContigsFile']", 'symmetrical': 'False'}),
            'data_set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.DataSet']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'estimated_ref_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'eukaryotic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'find_genes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '2048', 'null': 'True', 'blank': 'True'}),
            'min_contig': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'report_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'scaffolds': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'default_data_set': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quast_app.DataSet']"}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'estimated_ref_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'eukaryotic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'find_genes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'min_contig': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'scaffolds': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'quast_app.usersession': {
            'Meta': {'object_name': 'UserSession'},
            'default_data_set': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['quast_app.DataSet']"}),
            'estimated_ref_size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'eukaryotic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'find_genes': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_dirname': ('django.db.models.fields.CharField', [], {'max_length': '2048'}),
            'min_contig': ('django.db.models.fields.IntegerField', [], {'default': '500'}),
            'scaffolds': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['quast_app.User']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['quast_app']