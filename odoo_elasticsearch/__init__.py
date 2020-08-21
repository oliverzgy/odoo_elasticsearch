# -*- coding: utf-8 -*-

from . import controllers
from . import models
from xmlrpclib import MAXINT
from odoo.exceptions import MissingError

from odoo import api, fields
from odoo import models as Models


def field_convert_to_read_json(self, value, record, use_name_get=True):
    if isinstance(value, bytes):
        value = value.decode("utf-8")

    return '' if value is None else '' if value is False else value


def integer_convert_to_read_json(self, value, record, use_name_get=True):
    if value and value > MAXINT:
        return float(value)
    return value


def monetary_convert_to_read_json(self, value, record, use_name_get=True):
    return value


def reference_convert_to_read_json(self, value, record, use_name_get=True):
    return "%s,%s" % (value._name, value.id) if value else ""


def many2one_convert_to_read_json(self, value, record, use_name_get=True):
        if use_name_get and value:
            # evaluate name_get() as superuser, because the visibility of a
            # many2one field value (id and name) depends on the current record's
            # access rights, and not the value's access rights.
            try:
                # performance: value.sudo() prefetches the same records as value
                return {'id': value.id, 'uuid': value.uuid, 'name': value.sudo().display_name}
            except MissingError:
                # Should not happen, unless the foreign key is missing.
                return {'id': '', 'uuid': '', 'name': ''}
        else:
            return {'id': value.id or '', 'uuid': value.uuid or '', 'name': value.sudo().display_name or ''}


def relational_multi_convert_to_read_json(self, value, record, use_name_get=True):
        return [{'id': x.id, 'uuid': x.uuid, 'name': x.sudo().display_name} for x in value]


fields.Field.convert_to_read_json = field_convert_to_read_json
fields.Integer.convert_to_read_json = field_convert_to_read_json
fields.Monetary.convert_to_read_json = monetary_convert_to_read_json
fields.Reference.convert_to_read_json = reference_convert_to_read_json
fields.Many2one.convert_to_read_json = many2one_convert_to_read_json
fields._RelationalMulti.convert_to_read_json = relational_multi_convert_to_read_json


def read_json(self, fields=None, load='_classic_read'):
        """ read([fields])

        Reads the requested fields for the records in ``self``, low-level/RPC
        method. In Python code, prefer :meth:`~.browse`.

        :param fields: list of field names to return (default is all fields)
        :return: a list of dictionaries mapping field names to their values,
                 with one dictionary per record
        :raise AccessError: if user has no read rights on some of the given
                records
        """
        fields = self.check_field_access_rights('read', fields)

        # fetch stored fields from the database to the cache
        stored_fields = set()
        for name in fields:
            field = self._fields.get(name)
            if not field:
                raise ValueError("Invalid field %r on model %r" % (name, self._name))
            if field.store:
                stored_fields.add(name)
            elif field.compute:
                # optimization: prefetch direct field dependencies
                for dotname in field.depends:
                    f = self._fields[dotname.split('.')[0]]
                    if f.prefetch and (not f.groups or self.user_has_groups(f.groups)):
                        stored_fields.add(f.name)
        self._read(stored_fields)

        # retrieve results from records; this takes values from the cache and
        # computes remaining fields
        data = [(record, {'id': record._ids[0], 'uuid': record.uuid}) for record in self]
        use_name_get = (load == '_classic_read')
        for name in fields:
            convert = self._fields[name].convert_to_read_json
            for record, vals in data:
                # missing records have their vals empty
                if not vals:
                    continue
                try:
                    vals[name] = convert(record[name], record, use_name_get)
                except MissingError:
                    vals.clear()
        result = [vals for record, vals in data if vals]

        return result


@api.model
def search_read_json(self, domain=None, fields=None, offset=0, limit=None, order=None):
    """
    Performs a ``search()`` followed by a ``read()``.

    :param domain: Search domain, see ``args`` parameter in ``search()``. Defaults to an empty domain that will match all records.
    :param fields: List of fields to read, see ``fields`` parameter in ``read()``. Defaults to all fields.
    :param offset: Number of records to skip, see ``offset`` parameter in ``search()``. Defaults to 0.
    :param limit: Maximum number of records to return, see ``limit`` parameter in ``search()``. Defaults to no limit.
    :param order: Columns to sort result, see ``order`` parameter in ``search()``. Defaults to no sort.
    :return: List of dictionaries containing the asked fields.
    :rtype: List of dictionaries.

    """
    records = self.search(domain or [], offset=offset, limit=limit, order=order)
    if not records:
        return []

    if fields and fields == ['id']:
        # shortcut read if we only want the ids
        return [{'id': record.id, 'uuid': record.uuid} for record in records]

    # read() ignores active_test, but it would forward it to any downstream search call
    # (e.g. for x2m or function fields), and this is not the desired behavior, the flag
    # was presumably only meant for the main search().
    # TODO: Move this to read() directly?
    if 'active_test' in self._context:
        context = dict(self._context)
        del context['active_test']
        records = records.with_context(context)

    result = records.read_json(fields)
    if len(result) <= 1:
        return result

    # reorder read
    index = {vals['id']: vals for vals in result}
    return [index[record.id] for record in records if record.id in index]


Models.BaseModel.read_json = read_json
Models.BaseModel.search_read_json = search_read_json
