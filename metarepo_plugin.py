"""
metarepo_plugin.py - Airflow plugin for managing tables in metadata repository

Version History:
0.2 jwd3 11/11/2016 Hotfix
    Added SQLA scoped_session
0.3 jwd3 11/14/2016
    Added ValidValueView
    Added WorkflowConfigView
    Added SourceIngestionView
0.3.1 jwd3 01/17/2017
    Changed SourceIngesionView to ImportDefinitionView
0.3.2 jwd3 01/24/2017
    Added column label for ODS retention period in ImportDefinitionView
    Added additional columns to exclude in the ImportDefinition form dw_tables,ods_loads,stage_loads,file_downloads
    Changed variable names from Source Ingestion to Import Definition
"""
# This is the class you derive to create a plugin
from airflow.plugins_manager import AirflowPlugin

from flask_admin.contrib.sqla import ModelView
# from flask import Blueprint
# from flask_admin import BaseView, expose
# from flask_admin.base import MenuLink
# from flask_wtf import Form

import ast
from wtforms.fields import StringField
from airflow.www import utils as wwwutils

from sqlalchemy.orm import sessionmaker, scoped_session

from repository.metadata.models import FileCleanup, WorkflowConfig, ValidValue, ImportDefinition
from repository.connection import repo_engine

__version__ = "0.3.2"
__date__ = '2016-10-20'
__updated__ = '2017-01-24'


def get_session():
    session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=repo_engine))
    return session()


class SecureModelView(wwwutils.SuperUserMixin, ModelView):
    column_exclude_list = ['created_dttm','modified_dttm','etag']
    form_excluded_columns = ['created_dttm','modified_dttm','etag']


class FileCleanupView(SecureModelView):
    column_searchable_list = ['path', 'filename_pattern','archive_path']
    column_display_pk = True
    column_default_sort = 'rule_id'
    # column_editable_list = ['active_flg',]  # Causes 404 Missing CRSF token
    form_choices = {
        'cleanup_action': [
            ('A', 'A'),
            ('D', 'D'),
            ('Z', 'Z'),
        ]
    }

file_cleanup_view = FileCleanupView(FileCleanup,
                                    get_session(),
                                    name="File Cleanup",
                                    category="Metadata Repository")


class ParamValueField(StringField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = ast.literal_eval(valuelist[0])
            except:
                self.data = str(valuelist[0])
        else:
            self.data = ''


class WorkflowConfigView(SecureModelView):
    # form_create_rules = ('workflow_name', 'parameter_name', 'parameter_value')
    column_searchable_list = ['workflow_name','parameter_name']
    # column_display_pk = True
    column_default_sort = 'id'
    column_sortable_list = ['workflow_name','parameter_name']
    # column_editable_list = ['active_flg',]  # Causes 404 Missing CRSF token

    # column_list = ('workflow_name', 'parameter_name', 'parm_value')

    # Define label for dummy column
    column_labels = {
        'workflow_name': 'Workflow Name',
        'parameter_name': 'Parameter Name',
        'parameter_value': 'Parameter Value',
    }

    # form_overrides = dict(parameter_value=PickleField)
    def scaffold_form(self):
        form_class = super(WorkflowConfigView, self).scaffold_form()
        form_class.parameter_value = ParamValueField('parameter_value')
        return form_class

workflow_config_view = WorkflowConfigView(WorkflowConfig,
                                          get_session(),
                                          name="Workflow Config",
                                          category="Metadata Repository")


class ValidValueView(SecureModelView):
    column_searchable_list = ['category', 'attribute_name','valid_value']
    column_display_pk = False
    column_default_sort = 'attribute_name'
    # column_editable_list = ['active_flg',]  # Causes 404 Missing CRSF token


valid_value_view = ValidValueView(ValidValue,
                                  get_session(),
                                  name="Valid Values",
                                  category="Metadata Repository")


class ImportDefinitionView(SecureModelView):
    column_searchable_list = ['source_group_name','source_name','source_type','ingest_frequency']
    column_display_pk = False
    column_default_sort = 'source_name'
    column_sortable_list = ['source_group_name','source_name','source_type','ingest_frequency']
    column_exclude_list = ['created_dttm','modified_dttm','etag','source_definition']
    form_excluded_columns = ['created_dttm','modified_dttm','etag','source_definition',
                             'dw_tables','ods_loads','stage_loads','file_downloads']
    column_labels = {
        'ods_retention_period': 'ODS Retention Period',
    }

import_definition_view = ImportDefinitionView(ImportDefinition,
                                              get_session(),
                                              name="Import Definition",
                                              category="Metadata Repository")


# bp = Blueprint(
#     "file_cleanup", __name__,
#     template_folder='templates', # registers airflow/plugins/templates as a Jinja template folder
#     static_folder='static',
#     static_url_path='/static/file_cleanup')

# ml = MenuLink(
#     category='Metadata Repository',
#     name='Test Menu Link',
#     url='http://pythonhosted.org/airflow/')

# Defining the plugin class
class AirflowTestPlugin(AirflowPlugin):
    name = "metarepo_plugin"
    # operators = [PluginOperator]
    flask_blueprints = []
    # hooks = [PluginHook]
    # executors = [PluginExecutor]
    admin_views = [file_cleanup_view, workflow_config_view, valid_value_view, import_definition_view]
    # menu_links = [ml]
