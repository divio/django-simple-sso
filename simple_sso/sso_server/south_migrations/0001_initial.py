# -*- coding: utf-8 -*-
import datetime
from django.conf import settings
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Consumer'
        db.create_table('sso_server_consumer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('private_key', self.gf('django.db.models.fields.CharField')(default='zCZK89Dk5gFNVxt6Po3FYooDRUgIr8lkPqq8vDUJjBIIeRQKP1kAlsfGGY9kpuCW', unique=True, max_length=64)),
            ('public_key', self.gf('django.db.models.fields.CharField')(default='BL7olRs8N2nN1a4fuhuAECASZG3ERgMH4GmdqI8dkUg79Ay80FBxERICTAoMWmg1', unique=True, max_length=64)),
        ))
        db.send_create_signal('sso_server', ['Consumer'])

        # Adding model 'Token'
        db.create_table('sso_server_token', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('consumer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tokens', to=orm['sso_server.Consumer'])),
            ('request_token', self.gf('django.db.models.fields.CharField')(default='FOcGALzcHN4D1Fl4RjsOnUUOSIK71QhHhWhLY9EpsrZ5xIJIBHvfZRGCM9KPMkZI', unique=True, max_length=64)),
            ('access_token', self.gf('django.db.models.fields.CharField')(default='6iOTXc4LLS3fPIJl8wXmfsYPMm6wuwsvUQf7UTVnMX6TeFBpIM4apGOdKiHz8qUt', unique=True, max_length=64)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('redirect_to', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[getattr(settings, 'AUTH_USER_MODEL', 'auth.User')], null=True)),
        ))
        db.send_create_signal('sso_server', ['Token'])


    def backwards(self, orm):
        # Deleting model 'Consumer'
        db.delete_table('sso_server_consumer')

        # Deleting model 'Token'
        db.delete_table('sso_server_token')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sso_server.consumer': {
            'Meta': {'object_name': 'Consumer'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'private_key': ('django.db.models.fields.CharField', [], {'default': "'yPw6AHFmcPFosghzRA2v14JjHjhgEoLlzmOI2luovaZPechIRBDJrRbhQOyJAyaB'", 'unique': 'True', 'max_length': '64'}),
            'public_key': ('django.db.models.fields.CharField', [], {'default': "'AK35mZLc8n1yKnNMRDqgyrOo31NoSCT1ZqnmZE9UeJZQEjmi8mSmjQmZdqOnLX4o'", 'unique': 'True', 'max_length': '64'})
        },
        'sso_server.token': {
            'Meta': {'object_name': 'Token'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "'L8sKiHFRPEL6bN3R1QK2KHDDZ2F2MfyZcJrSr8GkYk64AFa9t0ZTpCw7zbUQiOmF'", 'unique': 'True', 'max_length': '64'}),
            'consumer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tokens'", 'to': "orm['sso_server.Consumer']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'redirect_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'request_token': ('django.db.models.fields.CharField', [], {'default': "'Es5jnmA77SZcy6dqdbSYGBg62iyPKisEkbd7w2RQsAxPAd8qYnewfPTGEgNGI71J'", 'unique': 'True', 'max_length': '64'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'})
        }
    }

    complete_apps = ['sso_server']
