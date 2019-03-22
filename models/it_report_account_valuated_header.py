# -*- coding: utf-8 -*-
import json
import logging
from odoo import models, fields, api


class ItInvoiceHeaderReport(models.Model):
    _name = 'it.units.header.report'
    _description = "Reporte Unidades Fisicas invoice"
    # DETALLE
    units_detalle = fields.One2many('it.report.physical.units', 'units_header_id', 'Detalle reporte')
    # DATOS CABECERA

    date_in = fields.Date(string='Fecha inicio')
    date_out = fields.Date(string='Fecha fin')
    vat = fields.Char(string='RUC')
    business_name = fields.Many2one('res.company', string='Razon Social')

    txt_binary = fields.Binary(string='Descargar Txt Sunat')

    @api.onchange("business_name")
    def _compute_it_ruc(self):
        self.vat = self.business_name.partner_id.vat or ""

    @api.multi
    def btnCalc(self):
        pass
