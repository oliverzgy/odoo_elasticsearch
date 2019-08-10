# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models
from odoo.tools.profiler import profile
from odoo.addons.odoo_elasticsearch.tools import index
from odoo.exceptions import UserError

_logging = logging.getLogger(__name__)


class IndexManagementkWizard(models.TransientModel):
    _name = "index.management.wizard"
    _description = "Index Management Wizard"

    name = fields.Char('名称', compute='_compute_name', store=True)
    index_ids = fields.Many2many('search.engine.index', string='索引')
    option = fields.Selection([
        ('create_all_indexes','创建全部索引'),
        ('create_relevant_indexes','创建相关索引'),
        ('create_all_documents','添加全部文件'),
        ('create_relevant_documents','添加相关文件'),
        ('update_all_documents','更新全部文件'),
        ('update_relevant_documents','更新相关文件'),
        ('delete_relevant_indexes','删除选中索引')
    ], string='选项', required=True) # 选项值必须与对应方法名称相同

    @api.depends('create_date')
    def _compute_name(self):
        for rec in self:
            rec.name = "索引管理-%s" % fields.Datetime.now()

    @api.multi
    @profile
    def action_confirm(self):
        self.ensure_one()
        string = 'self.%s()' % self.option
        _logging.info(string)
        return eval(string)


    @api.model
    def default_get(self, fields):
        res = super(IndexManagementkWizard, self).default_get(fields)
        res['index_ids'] = self._context and self._context.get('active_ids')
        return res

    @api.multi
    def create_all_indexes(self):
        index.create_all_indexes(self)

    @api.multi
    def create_relevant_indexes(self):
        index.create_relevant_indexes(self, self.index_ids)

    @api.multi
    def delete_relevant_indexes(self):
        for index_id in self.index_ids:
            if index_id.index_exists:
                index.delete_relevant_indexes(self, index_id)
        self.index_ids.unlink()

    @api.multi
    def create_all_documents(self):
        index.create_all_documents(self)

    @api.multi
    def create_relevant_documents(self):
        index.create_relevant_documents(self, self.index_ids)

    @api.multi
    def update_all_documents(self):
        index.update_all_documents()

    @api.multi
    def update_relevant_documents(self):
        index.update_relevant_documents(self, self.index_ids)
