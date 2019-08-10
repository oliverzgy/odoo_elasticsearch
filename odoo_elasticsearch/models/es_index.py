# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning, UserError, DeferredException

_logger = logging.getLogger(__name__)


class EsIndex(models.Model):
    _inherit = 'es.mixin'
    _name = 'es.index'
    _description = 'ES Index'

    name = fields.Char('Name', readonly=True, compute='_compute_name', compute_sudo=True, store=True)
    model_id = fields.Many2one('ir.model', string='Model', required=True)
    model_name = fields.Char(string='Model', related='model_id.model', store=True)
    suffix = fields.Char('Suffix', compute='_compute_name', compute_sudo=True, store=True)
    active = fields.Boolean('Active', default=True)
    index_info = fields.Text('Index Info', readonly=True)
    index_exists = fields.Boolean('ES', readonly=True)
    fields_include = fields.Char('Fields Included')
    fields_simple = fields.Char('Fields Simple')
    fields_complex = fields.Char('Fields Complex')
    mapping = fields.Text('Mapping')
    settings = fields.Text('Setting')

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _('Index must be unique!'))
    ]

    @api.depends('model_id')
    def _compute_name(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        database_uuid = ICPSudo.get_param('database.uuid')
        suffix = "%s" % (database_uuid[0:8])
        for rec in self:
            if rec.model_id:
                val = {
                    'name': "%s-%s" % (rec.model_id.model.replace('.','-'), suffix),
                    'suffix': suffix
                }
                rec.update(val)
        return True

    @api.one
    def action_bulk_document(self):
        self._bulk_document()

    @api.multi
    def _prepare_bulk_document(self, records):
        data = []
        for rec in self:
            for r in records:
                val1 = {"update": {"_id": r['id'], "_index": r.name, '_type': '_doc'}}
                val2 = {"doc": r, "doc_as_upsert": True}
                data.append(val1)
                data.append(val2)
        return data

    @api.one
    def _bulk_document(self):
        limit = 1024
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns + 1):
            records = model_obj.search_read_json([], fields=eval(self.fields_include) if self.fields_include else [],
                                                 limit=limit, offset=limit * i, order='id DESC')
            if records:
                self.bulk_document(body=self._prepare_bulk_document(records), refresh=True, index=self.name)
        return True

    @api.one
    def action_create_document(self):
        self._create_document()

    @api.one
    def _create_document(self):
        limit = 16
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns+1):
            records = model_obj.search_read_json([], fields=eval(self.fields_include) if self.fields_include else [], limit=limit, offset=limit*i, order='id DESC')
            for r in records:
                if not self.exists_document(index=self.name, doc_type='_doc', id=r['id']):
                    res = self.create_document(index=self.name, doc_type='_doc', id=r['id'], body=r, refresh=True)

        return True

    @api.one
    def action_update_document(self):
        self._update_document()

    @api.one
    def _update_document(self):
        limit = 16
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns + 1):
            records = model_obj.search_read_json([], fields=eval(self.fields_include) if self.fields_include else [], limit=limit, offset=limit * i, order='id DESC')
            for r in records:
                if self.exists_document(index=self.name, doc_type='_doc', id=r['id']):
                    res = self.update_document(index=self.name, doc_type='_doc', id=r['id'], body={'doc': r}, refresh=True)

        return True

    @api.one
    def create_document_simple(self):
        self._create_document_simple()

    @api.one
    def _create_document_simple(self):
        limit = 100
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns+1):
            records = model_obj.search_read_json([], fields=eval(self.fields_simple) if self.fields_simple else [], limit=limit, offset=limit*i, order='id DESC')
            for r in records:
                if not self.exists_document(index=self.name, doc_type='_doc', id=r['id']):
                    res = self.create_document(index=self.name, doc_type='_doc', id=r['id'], body=r, refresh=True)

        return True

    @api.one
    def update_document_simple(self):
        self._update_document_simple()

    @api.one
    def _update_document_simple(self):
        limit = 100
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns + 1):
            records = model_obj.search_read_json([], fields=eval(self.fields_simple) if self.fields_simple else [], limit=limit, offset=limit * i, order='id DESC')
            for r in records:
                if self.exists_document(index=self.name, doc_type='_doc', id=r['id']):
                    res = self.update_document(index=self.name, doc_type='_doc', id=r['id'], body={'doc': r}, refresh=True)

        return True

    @api.one
    def update_document_complex(self):
        limit = 16
        model_obj = self.env[self.model_name]
        record_count = model_obj.search_count([])
        _logger.info('Model records: %s', record_count)
        turns = record_count // limit

        for i in range(0, turns + 1):
            records = model_obj.search_read_json([], fields=eval(self.fields_complex) if self.fields_complex else [],
                                                 limit=limit, offset=limit * i, order='id DESC')
            for r in records:
                if self.exists_document(index=self.name, doc_type='_doc', id=r['id']):
                    res = self.update_document(index=self.name, doc_type='_doc', id=r['id'], body={'doc': r},
                                                   refresh=True)

        return True

    @api.one
    def delete_document(self):
        pass

    @api.one
    def action_create_index(self):
        if not self.exists_index(index=self.name):
            res = self.create_index(index=self.name, body=eval(str.strip(self.settings)) if self.settings else None)
            if self.settings:
                self.put_settings()
            if self.mapping:
                self.put_mapping()
            self.index_exists = True
            return res
        else:
            self.index_exists = True
            return True

    @api.one
    def action_refresh_index(self):
        res = self.refresh_index(index=self.name)
        print(res)
        return res

    @api.one
    def action_delete_index(self):
        res = self.delete_index(index=self.name)
        print(res)
        self.index_exists = False
        return res

    @api.one
    def action_get_index(self):
        res = self.get_index(index=self.name)
        self.index_info = res
        return res

    @api.one
    def action_close_index(self):
        res = self.close_index(index=self.name)
        print(res)
        return res

    @api.one
    def action_open_index(self):
        res = self.open_index(index=self.name)
        print(res)
        return res

    @api.one
    def action_check_index(self):
        res = self.exists_index(index=self.name)
        self.index_exists = res
        return res

    @api.one
    def action_put_mapping(self):
        if not self.mapping:
            return True
        if not isinstance(eval(str.strip(self.mapping)), dict):
            raise ValidationError(_('Mapping info must be a dictionary: {key:value}'))

        body = eval(str.strip(self.mapping))
        res = self.put_mapping(index=self.name, doc_type='_doc', body=body)
        return res

    @api.one
    def action_put_settings(self):
        if not self.settings:
            return True
        if not isinstance(eval(str.strip(self.settings)), dict):
            raise ValidationError(_('Setting info must be a dictionary： {key:value}'))

        body = eval(str.strip(self.settings))
        self.close_index(index=self.name)
        res = self.put_setting(index=self.name, body=body)
        self.open_index(index=self.name)
        return res
