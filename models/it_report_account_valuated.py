# -*- coding: utf-8 -*-
from odoo import models, fields, api


class UnidadesFisicas(models.Model):
    _name = "it.report.inventory.valuated"
    _description = "Reporte Inventario Valorizado"

    # ID HEADER UNIDADES FISICAS
    valuated_header_id = fields.Many2one('it.inventory.header.report', 'valuated header')

    date = fields.Char(string='Fecha')
    type_comprobante = fields.Char(string='Tipo (Tabla 10)')
    series = fields.Char(string='Serie')
    number = fields.Char(string='Correlativo')  # se cambio xq lo pedio Katty
    operation_type = fields.Char(string='Tipo de operacion (Tabla 12)')
    product = fields.Char(string='Producto')

    # ENTRADAS
    input_number = fields.Float(string='Entradas')
    # SALIDAS
    output_quantity = fields.Float(string='Salidas')
    # FINAL
    final_total_cost = fields.Float(string='Saldo Final')

    txt_full_columns = fields.Text()
