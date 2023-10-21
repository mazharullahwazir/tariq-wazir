from odoo import models, fields, api


class ParticularReport(models.AbstractModel):
    _name = 'report.mrp_repair_order_print.report_repairorder_report'
    _description = 'repair order print'

    @api.model
    def _get_report_values(self, docids, data=None):

        main_information ={}
        header =[]
        body =[]
        fees_lines =[]
        
        mapped = True
        repair_obj=self.env['repair.order']
        
        mapped_helpdesk_ticket =repair_obj.browse(docids).mapped('ticket_id')
        
        if not mapped_helpdesk_ticket:
            mapped_helpdesk_ticket =self.env['repair.order'].browse(docids)
            mapped = False
        for t in mapped_helpdesk_ticket:
            if mapped ==True:
                helpdesk_ticket= repair_obj.search([('ticket_id','=',t.id)])
            else:
                helpdesk_ticket =mapped_helpdesk_ticket

         #header information
       
            header_information = {
                    'state': helpdesk_ticket[0].state,
                    # 'partner_invoice_id' : helpdesk_ticket[0].partner_invoice_id,
                    'partner_id' : helpdesk_ticket[0].partner_id,
                    'address_id':helpdesk_ticket[0].address_id,
                    'product_to_repair': helpdesk_ticket[0].product_id.display_name,
                    'lot_id' : helpdesk_ticket[0].lot_id,
                    'guarantee_limit' : helpdesk_ticket[0].guarantee_limit,
                    'currency_id' : helpdesk_ticket[0].pricelist_id.currency_id
                    
                 }
            
            header.append(header_information)
            
            discount = 0.00
            total_amount_untaxed =0.00
            total_amount_tax = 0.00
            total_sum = 0.00
            for line in helpdesk_ticket:
                if line.invoice_method !='none':
                    
                    total_amount_untaxed +=line.amount_untaxed
                    total_amount_tax += line.amount_tax
                    total_sum +=line.amount_total
                for operation in line.operations:
                   
                    boday_vals = {
                                'operations': operation,
                                }
                    body.append(boday_vals)
                for operation2 in line.fees_lines:
                    discount +=operation2.discount    
                    boday_vals2 = {
                                      
                                'fees_lines': operation2,
                                }
                    fees_lines.append(boday_vals2)
            header.append({
#                             'order_name' : helpdesk_ticket[0].display_name,
                            'order_name' : helpdesk_ticket[0].ticket_id.display_name,
                           'discount':discount,
                           'total_amount_untaxed' : total_amount_untaxed,
                           'total_amount_tax': total_amount_tax,
                           'total_sum': total_sum,
                           })
        
        return {
            'header':header,
            'body': body,
            'body2':fees_lines,
        }

        
        
        