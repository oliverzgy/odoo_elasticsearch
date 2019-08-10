# -*- coding: utf-8 -*-

import requests
import re
from elasticsearch import Elasticsearch
from elasticsearch.client import IndicesClient, IngestClient, ClusterClient, NodesClient, CatClient, SnapshotClient, TasksClient
import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError, DeferredException

_logger = logging.getLogger(__name__)


class EsMixin(models.AbstractModel):
    _name = 'es.mixin'
    _description = 'ES Mixin'

    @api.model
    def _get_es_credential(self):
        res = {}
        ICPSudo = self.env['ir.config_parameter'].sudo()
        elasticsearch_http = ICPSudo.get_param('elasticsearch.http')
        elasticsearch_url = ICPSudo.get_param('elasticsearch.url')
        elasticsearch_user = ICPSudo.get_param('elasticsearch.user')
        elasticsearch_pass = ICPSudo.get_param('elasticsearch.pass')

        if not elasticsearch_url:
            raise ValidationError(_(u"Elasticsearch URL not provided!"))

        res.update(
            elasticsearch_http= elasticsearch_http,
            elasticsearch_url= elasticsearch_url,
            elasticsearch_user=elasticsearch_user or '',
            elasticsearch_pass=elasticsearch_pass or ''
        )
        return res

    @api.model
    def _prepare_es_connection(self):
        credential = self._get_es_credential()
        http = credential.get('elasticsearch_http')
        url = credential.get('elasticsearch_url')
        user = credential.get('elasticsearch_user')
        secret = credential.get('elasticsearch_pass')
        url = "%s://%s:%s@%s/" % (http, user, secret, url)  # for basic auth
        es = Elasticsearch([url])
        return es

    # index management

    @api.model
    def create_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.create
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).create(**kwargs)
        return res

    @api.model
    def delete_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.delete
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).delete(**kwargs)
        return res

    @api.model
    def get_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.get
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).get(**kwargs)
        return res

    @api.model
    def exists_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.exists
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).exists(**kwargs)
        return res

    @api.model
    def put_mapping(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.put_mapping
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).put_mapping(**kwargs)
        return res

    @api.model
    def put_setting(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.put_setting
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).put_settings(**kwargs)
        return res

    @api.model
    def close_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.close
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).close(**kwargs)
        return res

    @api.model
    def open_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.open
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).open(**kwargs)
        return res

    @api.model
    def put_template(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.put_template
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).put_template(**kwargs)
        return res

    @api.model
    def refresh_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.refresh
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).refresh(**kwargs)
        return res

    @api.model
    def upgrade_index(self, **kwargs):
        """
        http://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.client.IndicesClient.upgrade
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = IndicesClient(es).upgrade(**kwargs)
        return res

    # document management

    @api.model
    def create_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.create
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.create(**kwargs)
        return res

    @api.model
    def bulk_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.Elasticsearch.bulk
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.bulk(**kwargs)
        return res

    @api.model
    def delete_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.delete
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.delete(**kwargs)
        return res

    @api.model
    def exists_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.exists
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.exists(**kwargs)
        return res

    @api.model
    def exists_source_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.exists_source
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.exists_source(**kwargs)
        return res

    @api.model
    def get_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.get
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.get(**kwargs)
        return res

    @api.model
    def get_source_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.get_source
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.get_source(**kwargs)
        return res

    @api.model
    def index(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.index
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.index(**kwargs)
        return res

    @api.model
    def reindex(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.reindex
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.reindex(**kwargs)
        return res

    @api.model
    def msearch_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.msearch
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.msearch(**kwargs)
        return res

    @api.model
    def put_template(self, **kwargs):
        es = self._prepare_es_connection()
        res = es.put_template(**kwargs)
        return res

    @api.model
    def scroll_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.scroll
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.scroll(**kwargs)
        return res

    @api.model
    def search_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.search
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.search(**kwargs)
        return res

    @api.model
    def search_count(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.count
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.count(**kwargs)
        return res

    @api.model
    def update_document(self, **kwargs):
        """
        https://elasticsearch-py.readthedocs.io/en/stable/api.html#elasticsearch.Elasticsearch.update
        :param kwargs:
        :return:
        """
        es = self._prepare_es_connection()
        res = es.update(**kwargs)
        return res
