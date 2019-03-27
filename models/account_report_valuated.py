# -*- coding: utf-8 -*-
from odoo import models, fields, api


class XlsxMoveHeaderReport(models.AbstractModel):
    _name = "report.report_xlsx.it.inventory.header.report_xlsx"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, move):
        for obj in move:
            # CREAR LA CABECERA
            name = 'Inventario Valorizado - %s' % (obj.date_in)
            sheet = workbook.add_worksheet(name)
            font_titulo_empresa = workbook.add_format(
                {
                    'bold': True,
                    'font_color': '#0B173B',
                    'font_size': 14,
                    'border': 4,
                    'align': 'center',
                    'valign': 'vcenter'
                })
            sheet.merge_range('A1:I4', self.env.user.company_id.name, font_titulo_empresa)
            # REPORTE STOCK MOVE
            stock_move_before = self.env["stock.move"].search(
                [("date", ">=", obj.date_in_time), ("date", "<=", obj.date_out_time)])

            array_main = []
            contador = 0
            map_products_before = {}
            for before_in in stock_move_before:
                if before_in.product_id.id is not False:
                    str_product_id = str(before_in.product_id.id)
                    if str_product_id not in map_products_before:
                        map_products_before.update({str_product_id: 0})
                    value_stock = map_products_before[str_product_id] or 0
                    a = before_in.location_id.usage
                    b = before_in.location_dest_id.usage
                    if (a == 'internal') and (b != 'internal'):
                        value_stock - before_in.product_uom_qty or 0
                    if (a == 'internal') and (b == 'internal'):
                        pass
                    if (a != 'internal') and (b == 'internal'):
                        value_stock + before_in.product_uom_qty or 0
                    map_products_before[str_product_id] = value_stock
                array_field = []
                array_field.append(before_in.date)
                array_field.append(before_in.picking_id.catalog_01_id.code or "")
                array_field.append(before_in.picking_id.series.series or "")
                array_field.append(before_in.picking_id.correlative or "")
                array_field.append(before_in.product_id.name)
                array_field.append(before_in.product_id.uom_id.code_unit_measure.code or "")
                array_field.append("")
                array_field.append("")
                array_field.append(before_in.date)
                array_main.append(array_field)
                contador = contador + 1
            sheet.set_column('A:I', 8)
            row_name = 'A8:I%s' % (int(contador + 8))
            sheet.add_table(row_name, {'data': array_main, 'columns': [{'header': 'FECHA'},
                                                                       {'header': 'T. Doc. Comp'},
                                                                       {'header': 'Serie Doc'},
                                                                       {'header': 'Numero Doc'},
                                                                       {'header': 'Producto'},
                                                                       {'header': 'T. Operacion'},
                                                                       {'header': 'Entradas'},
                                                                       {'header': 'Salidas'},
                                                                       {'header': 'Saldo Final'},
                                                                       ]})
