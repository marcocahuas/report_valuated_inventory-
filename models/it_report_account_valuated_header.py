# -*- coding: utf-8 -*-
import base64
import datetime
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ItInvoiceHeaderReport(models.Model):
    _name = 'it.inventory.header.report'
    _description = "Reporte Inventario Valorizado invoice"
    # DETALLE
    valuated_detalle = fields.One2many('it.report.inventory.valuated', 'valuated_header_id', 'Detalle reporte')
    # DATOS CABECERA

    date_in = fields.Date(string='Fecha inicio')
    date_out = fields.Date(string='Fecha fin')

    date_in_time = fields.Datetime(string='Fecha inicio2')
    date_out_time = fields.Datetime(string='Fecha fin2')
    vat = fields.Char(string='RUC')
    business_name = fields.Many2one('res.company', string='Razon Social')
    txt_filename = fields.Char()
    txt_binary = fields.Binary(string='Descargar Txt Sunat')

    @api.onchange("business_name")
    def _compute_it_ruc(self):
        self.vat = self.business_name.partner_id.vat or ""

    @api.multi
    def btnCalc(self):
        pass

    @api.multi
    def check_download_txt_sunat(self):
        content = ""
        count_sale = 0
        d_ref = datetime.datetime.strptime(self.date_out, "%Y-%m-%d")
        d_ref_out = datetime.datetime.strptime(self.date_out, "%Y-%m-%d")
        d_ref_in = datetime.datetime.strptime(self.date_in, "%Y-%m-%d")
        # d_ref = [datetime.datetime.fromtimestamp(self.date_out, "%Y-%m-%d")]
        month = "%02d" % (d_ref.month,)
        # DECLARAR FECHAS

        date_in_before = datetime.datetime.combine(datetime.date(d_ref_in.year, d_ref_in.month, d_ref_in.day),
                                                   datetime.time(0, 0, 0))
        date_out_after = datetime.datetime.combine(datetime.date(d_ref_out.year, d_ref_out.month, d_ref_out.day),
                                                   datetime.time(23, 59, 59))
        self.date_in_time = date_in_before
        self.date_out_time = date_out_after
        # date_in_before = datetime.datetime.combine(self.date_in, datetime.time(0, 0, 0))
        # date_out_after = datetime.datetime.combine(self.date_out, datetime.time(23, 59, 59))

        # 1. INFORMACION DE ENTRADA
        # SALDO INCIIAL

        stock_move_before = self.env["stock.move"].search([("date", "<", self.date_in_time)])
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

        # 2. GENERAR EL TXT
        stock_move_after = self.env["stock.move"].search(
            [("date", ">=", self.date_in_time), ("date", "<=", self.date_out_time)])

        for stock_out in stock_move_after:
            stringventas = "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s" % (
                str(d_ref.year) + "" + str(month) + "00",  # campo 1
                str("M") + str(stock_out.id),  # campo 2
                stock_out.product_id.it_existence.code or "",  # campo 6
                stock_out.product_id.it_existence.id or "",  # revisar el campo 7
                "",  # campo 8
                stock_out.picking_id.it_date_gr or "",  # campo 9
                stock_out.picking_id.catalog_01_id.code or "",  # campo 10
                stock_out.picking_id.series.id or "",  # campo 11
                stock_out.picking_id.correlative or "",  # campo 12
                stock_out.picking_id.type_transaction.id or "",  # campo 13
                stock_out.product_id.it_existence.description or "",  # campo 14
                stock_out.product_id.uom_id.code_unit_measure.code or "",  # campo 15
                stock_out.product_id.id or "0",  # SALDO INICIAL campo 16
                map_products_before[str_product_id],  # SALDO INICIAL campo 16

                "",  # campo 19

            )

            content += str(stringventas) + "\r\n"

        nametxt = 'LE%s%s%s%s%s%s%s%s%s%s.TXT' % (
            self.env.user.company_id.partner_id.vat,
            d_ref.year,  # Year
            month,  # Month
            '00',
            '140100',
            '00',
            '1',
            str(count_sale),
            '1',
            '1'
        )
        self.write({
            "txt_filename": nametxt,
            "txt_binary": base64.b64encode(bytes(content, "utf-8"))
        })
        return {
            "name": "Report",
            "type": "ir.actions.act_url",
            "url": "web/content/?model=" + self._name + "&id=" + str(
                self.id) + "&filename_field=file_name&field=txt_binary&download=true&filename=" + self.txt_filename,
            "target": "new",
        }
