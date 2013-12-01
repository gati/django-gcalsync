# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SyncedCalendar'
        db.create_table(u'gcalsync_syncedcalendar', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendar_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('last_synced', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'gcalsync', ['SyncedCalendar'])

        # Adding model 'SyncedEvent'
        db.create_table(u'gcalsync_syncedevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('gcal_event_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('gcal_event_url', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('origin', self.gf('django.db.models.fields.CharField')(default='google', max_length=6)),
            ('synced_calendar', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['gcalsync.SyncedCalendar'])),
        ))
        db.send_create_signal(u'gcalsync', ['SyncedEvent'])


    def backwards(self, orm):
        # Deleting model 'SyncedCalendar'
        db.delete_table(u'gcalsync_syncedcalendar')

        # Deleting model 'SyncedEvent'
        db.delete_table(u'gcalsync_syncedevent')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'gcalsync.syncedcalendar': {
            'Meta': {'object_name': 'SyncedCalendar'},
            'calendar_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'gcalsync.syncedevent': {
            'Meta': {'object_name': 'SyncedEvent'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'gcal_event_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'gcal_event_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'origin': ('django.db.models.fields.CharField', [], {'default': "'google'", 'max_length': '6'}),
            'synced_calendar': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gcalsync.SyncedCalendar']"})
        }
    }

    complete_apps = ['gcalsync']