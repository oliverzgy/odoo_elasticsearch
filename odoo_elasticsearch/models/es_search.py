# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class EsSearch(models.Model):
    _inherit = 'es.mixin'
    _name = 'es.search'
    _description = 'ES Search'

    @api.model
    def query(self, **kwargs):
        """
        定义搜索引擎搜索方法，以供应用调用
        :param kwargs:
        :return:
        """
        res = self.search_document(**kwargs)
        return res

    @api.model
    def count(self, **kwargs):
        """
        定义搜索引擎搜索方法，以供应用调用
        :param kwargs:
        :return:
        """
        res = self.search_count(**kwargs)
        return res



