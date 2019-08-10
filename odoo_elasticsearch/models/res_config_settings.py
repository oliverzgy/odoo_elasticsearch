# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    elasticsearch_http = fields.Selection([('http', 'http'),('https','https')],string=u'HTTP or HTTPS', default='http')
    elasticsearch_url = fields.Char(u'ES URL')
    elasticsearch_user = fields.Char(u'ES User', default='admin')
    elasticsearch_pass = fields.Char(u'ES Pass', default='admin')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update(
            elasticsearch_http=ICPSudo.get_param('elasticsearch.http'),
            elasticsearch_url=ICPSudo.get_param('elasticsearch.url'),
            elasticsearch_user = ICPSudo.get_param('elasticsearch.user'),
            elasticsearch_pass = ICPSudo.get_param('elasticsearch.pass')
        )

        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('elasticsearch.http', self.elasticsearch_http)
        ICPSudo.set_param('elasticsearch.url', self.elasticsearch_url)
        ICPSudo.set_param('elasticsearch.user', self.elasticsearch_user)
        ICPSudo.set_param('elasticsearch.pass', self.elasticsearch_pass)
