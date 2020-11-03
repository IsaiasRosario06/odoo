# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged, Form
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

@tagged('ncf', 'post_install', '-at_install')
class TestAccountMoveNCF(TransactionCase):
    def setUp(self):
        super(TestAccountMoveNCF, self).setUp()
        self.account_move = self.env['account.move']
    
    def test_ncf_char_min_length(self):
        '''Ensure form raises ValidationError exc if ncf length is lesser than 11 char'''
        account_move_form = Form(self.account_move)
            
        with self.assertRaises(ValidationError):
            account_move_form.ncf = 'XXXXXXXXXX'
            account_move_form.save()
            
    def test_ncf_char_max_length(self):
        '''Ensure the length of the NCF is equals to 11 even if it is given more characters, after saved'''
        form = Form(self.account_move)
        form.ncf = 'XXXXXXXXXXXXX'
        form.save()
        self.assertEqual(len(form.ncf), 11)
        
    def test_auto_ncf_save_sequence(self):
        '''Ensure that NCF is saved and next one is generated correctly afterwards (when assigned automatically)

        -Assuming gasto.menor sequence parameters:
        --Prefix	      B13
        --Sequence Size	  8
        --Step	          1
        --Next Number	  3
        '''
        
        form1 = Form(self.account_move)
        form1.ncf_type = 'gasto.menor'
        sequence = self.env['ir.sequence'].next_by_code(form1.ncf_type)
        form1.save()
        self.assertEqual(form1.ncf, sequence)
        
        form2 = Form(self.account_move)
        form2.ncf_type = 'gasto.menor'
        sequence = self.env['ir.sequence'].next_by_code(form2.ncf_type)
        form2.save()
        self.assertEqual(form2.ncf, sequence)
        
        form3 = Form(self.account_move)
        form3.ncf_type = 'gasto.menor'
        sequence = self.env['ir.sequence'].next_by_code(form3.ncf_type)
        form3.save()
        self.assertEqual(form3.ncf, sequence)
        
    def test_unique_ncf(self):
        '''Ensure an exception is raised if a NCF is already taken'''
        
        form1 = Form(self.account_move)
        form1.ncf_type ='gasto.menor'
        form1.save()
        
        form2 = Form(self.account_move)
        form2.ncf = form1.ncf
        
        with self.assertRaises(ValidationError):
            form2.save()
            
        
    def test_form_ncf_onchange(self):
        '''
        Testing if the NCF is the right one after triggering onchange on ncf_type
        '''
        
        self.account_move_form = Form(self.env['account.move'])
        
        self.account_move_form.ncf_type = 'gasto.menor'
        sequence = self.env['ir.sequence'].search([('code','=',self.account_move_form.ncf_type)])
        ncf = sequence.get_next_char(sequence.number_next_actual)
        self.assertEqual(self.account_move_form.ncf, ncf)
        
        self.account_move_form.ncf_type = 'con.final'
        sequence = self.env['ir.sequence'].search([('code','=',self.account_move_form.ncf_type)])
        ncf = sequence.get_next_char(sequence.number_next_actual)
        self.assertEqual(self.account_move_form.ncf, ncf)
        
        self.account_move_form.ncf_type = 'reg.especial'
        sequence = self.env['ir.sequence'].search([('code','=',self.account_move_form.ncf_type)])
        ncf = sequence.get_next_char(sequence.number_next_actual)
        self.assertEqual(self.account_move_form.ncf, ncf)
        
    def test_ncf_sequence_create(self):
        '''Try to create a ncf_sequence object.'''
        
        ncf_seq = self.env['ir.sequence'].create({
            'code':'test.ncf.sequence',
            'name':'test ncf'
        })
        self.assertTrue(ncf_seq)

    # account.move.type will be used to know which ncf sequences will be available.

        # selection=[
        #     ('entry', 'Journal Entry'),
        #     ('out_invoice', 'Customer Invoice'),
        #     ('out_refund', 'Customer Credit Note'),
        #     ('in_invoice', 'Vendor Bill'),
        #     ('in_refund', 'Vendor Credit Note'),
        #     ('out_receipt', 'Sales Receipt'),
        #     ('in_receipt', 'Purchase Receipt'),
        # ]


    # if move type is in ncf_sequence, the ncf_sequence must be able to be selected and
    # saved in an account_move of that type
    def test_move_type_in_ncf_sequence(self):
        
        form = Form(self.account_move)
        
        move_types = []
        move_types.append(self.env['ncf_generator.move_type'].search([('code','=',form.type)]).id)
        
        ncf_seq = self.env['ir.sequence'].create({
            'code':'test.ncf.seq',
            'name':'test ncf',
            'move_type_ids': move_types,
            'padding': 8,
            'number_increment': 1,
            'prefix':'XXX'
        })
        ncf = ncf_seq.get_next_char(ncf_seq.number_next_actual)
        
        form.ncf_type = ncf_seq.code
        form.save()
        self.assertEqual(ncf, form.ncf)

    # if move type is no in ncf_sequence, can't be selected in account_move
    def test_move_type_not_in_ncf_sequence(self):
        form = Form(self.account_move)
        
        move_types = []
        move_types.extend(move_type.id for move_type in self.env['ncf_generator.move_type'].search([]))
        _logger.info(f"move_types after extension => {move_types}")
        move_types.remove(self.env['ncf_generator.move_type'].search([('code','=',form.type)]).id)
        _logger.info(f"move_types after delete exclusion => {move_types}")
        
        ncf_seq = self.env['ir.sequence'].create({
            'code':'test.ncf.seq',
            'name':'test ncf',
            'move_type_ids': move_types,
            'padding': 8,
            'number_increment': 1,
            'prefix':'XXX'
        })

        with self.assertRaises(ValidationError):
            # Raise when move type isn't in ncf sequence
            form.ncf_type = ncf_seq.code
            form.save()