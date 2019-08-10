# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


MODEL_FILTER_DOMAIN = [
    ('transient', '!=', True), ('model', 'not in', ['res.users', 'hr.employee', '_unknown']),
    ('model', 'not ilike', 'ir.'),
    ('model', 'not ilike', 'mail.')
]

FIELD_FILTER_DOMAIN = [
    ('ttype', 'in', ['many2one', 'many2many', 'one2many'])
]


def get_relevant_models(self, model_ids):
    field_obj = self.env['ir.model.fields']
    model_obj = self.env['ir.model']
    FIELD_FILTER_DOMAIN.append(('model_id', 'in', model_ids.ids))
    field_ids = field_obj.search(FIELD_FILTER_DOMAIN)
    relevant_models = field_ids.mapped('relation')
    relevant_model_ids = model_obj.search([('model', 'in', relevant_models)])
    return relevant_model_ids


def create_all_indexes(self):
    index_obj = self.env['search.engine.index']
    model_obj = self.env['ir.model']

    index_ids = index_obj.search(['|', ('active', '=', True),('active', '=', False)])
    index_model_ids = index_ids.mapped('model_id')
    model_ids = model_obj.search(MODEL_FILTER_DOMAIN)

    todo_model_ids = model_ids - index_model_ids
    for model_id in todo_model_ids:
        val = {
            'model_id': model_id and model_id.id
        }
        index_id = index_obj.create(val)
        self._cr.commit()
        _logger.info('%s %s' % (model_id.model, index_id.name))
        index_id.create_index()

    return True


def create_relevant_indexes(self, index_ids):
    index_obj = self.env['search.engine.index']
    model_obj = self.env['ir.model']

    index_ids = index_obj.search([('id', 'in', index_ids.ids), '|', ('active', '=', True), ('active', '=', False)])
    index_model_ids = index_ids.mapped('model_id')

    relevant_model_ids = get_relevant_models(self, index_model_ids)
    model_ids = model_obj.search(MODEL_FILTER_DOMAIN)

    todo_model_ids = (model_ids & relevant_model_ids) - index_model_ids
    print(todo_model_ids)
    for model_id in todo_model_ids:
        val = {
            'model_id': model_id and model_id.id
        }
        index_id = index_obj.create(val)
        self._cr.commit()
        _logger.info('%s %s' % (model_id.model, index_id.name))
        index_id.create_index()

    return True


def create_all_documents(self):
    index_obj = self.env['search.engine.index']
    index_ids = index_obj.search([])
    for index_id in index_ids:
        index_id.create_document()
    return True


def create_relevant_documents(self, index_ids):
    for index_id in index_ids:
        index_id.create_document()
    return True


def update_all_documents(self):
    index_obj = self.env['search.engine.index']
    index_ids = index_obj.search([])
    for index_id in index_ids:
        index_id.update_document()
    return True


def update_relevant_documents(self, index_ids):
    for index_id in index_ids:
        index_id.update_document()
    return True


def delete_relevant_indexes(self, index_ids):
    for index_id in index_ids:
        index_id.delete_index()
    return True