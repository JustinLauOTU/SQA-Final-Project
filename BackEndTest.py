"""
=======================================================================================================================
Phase #5: Back-End Unit Tests
=======================================================================================================================

This is the python unit test file (specifically for white-box testing) using the unittest framework

----How to run----
Make sure you are in the project root folder, then type:
    
        python -m pytest BackEndTest.py -v

or
        python test BackEndTest.py

You will see PASS / FAIL for each test

"""

import sys
import os
import unittest 

#-------------------------- Path Setup --------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "Backend"))
from Backend import read #module we are testing


# Helper functions that will create and delete temp files 
def _make_temp_files(path, content):
    with open(path, 'w') as f: 
        f.write(content)
    return path

def _remove_temp_files(path):
    if os.path.exists(path):
        os.remove(path)

"""
======================================================================================================================
STATEMENT COVERAGE - read_transactions()
======================================================================================================================

Every line inside read_transactions() will execute at least once across all the test cases combined
"""
class TestReadTransactions(unittest.TestCase):
    
    # To help set a filename for a temp file
    def setUp(self):
        self.tmp = "tmp_transactions.aft"

    # Call function to remove file
    def tearDown(self):
        _remove_temp_files(self.tmp)
    
    # T1 test - Empty file
    def test_T1_empty_file(self):
        
        _make_temp_files(self.tmp, "")
        result = read.read_transactions(self.tmp)
        self.assertEqual(result, [], 
                         "An empty file should produce zero transactions")

    # T2 test - one perfectly valid transaction line
    def test_T2_one_valid_transaction(self):
        code = "04"
        name = "John Smith".ljust(20)
        acct = "12345"
        funds = "00500.00"
        pad = "   "
        line = f"{code} {name} {acct} {funds}{pad}"
        self.assertEqual(len(line), 41, "Test line itself is wrong length - fix the test!" )
        _make_temp_files(self.tmp, line + "\n")
        
        result = read.read_transactions(self.tmp)
        
        self.assertEqual(len(result), 1,
                         "Should have parsed exactly one transaction.")
        self.assertEqual(result[0]['transaction_code'], '04' )
        self.assertEqual(result[0]['account_number'], '12345')
        self.assertEqual(result[0]['funds_involved'], 500.0)

    # T3 test - Line with wrong length (too short) 
    def test_T3_line_wrong_length(self):
        short_line = "04 TooShort\n"
        _make_temp_files(self.tmp, short_line)
        
        result = read.read_transactions(self.tmp)
        
        self.assertEqual(result, [],
                         "A line with wrong length should be skipped entirely.")

    # T4 - Two valid lines (loop will run more than once)
    def test_T4_empty_line(self):
        line1 = f"04 {'John Smith'.ljust(20)} 12345 00500.00   "
        line2 = f"01 {'Jane Doe'.ljust(20)} 67890 00100.00   "
        
        self.assertEqual(len(line1), 41,
                         "Test line itself is wrong length - fix the test!" )
        self.assertEqual(len(line2), 41,
                         "Test line itself is wrong length - fix the test!" )
        
        content = line1 + "\n" + line2 + "\n"
        _make_temp_files(self.tmp, content)
        
        result = read.read_transactions(self.tmp)
        
        self.assertEqual(len(result), 2,
                         "Two valid lines should produce 2 transactions.")
        self.assertEqual(result[0]['transaction_code'], '04' )
        self.assertEqual(result[1]['transaction_code'], '01')

    # T5 test - Line that looks 41 chars but has an unparseable funds field
    def test_T5_unparseable(self):
        bad_line = f"04 {'John Smith'.ljust(20)} 12345 NOTANUM!   "
        self.assertEqual(len(bad_line), 41,
                         "Test line itself is wrong length - fix the test!" )
        _make_temp_files(self.tmp, bad_line + "\n")
        
        result = read.read_transactions(self.tmp)
        
        self.assertEqual(result, [],
                         "A line with non-numeric funcs should be caught and skipped entirely.")
    

# =======================================================================================================================
# DECISION + LOOP COVERAGE - apply_transactions()
# =======================================================================================================================

class TestApplyTransactions(unittest.TestCase):
    
    # Helper function: make a minimal account dict
    def _make_account(self, num="12345", name="Test User", status = "A", balance = 1000.0, txns = 0, plan = "SP"):
        return {
            'account_number': num,
            'name' : name,
            'status' : status,
            'balance': balance,
            'total_transactions': txns,
            'plan': plan
        }

    # Helper function: make a minimal transaction dict
    def _make_transactions(self, code, acct = "12345", funds = 100.0, name = "Test User"):
        return {
            'transaction_code': code,
            'account_number': acct,
            'funds_involved': funds,
            'name': name,
        }

    # D0 - Empty transaction list (outer loop runs zero times)
    def test_D0_empty_transactions(self):
        accounts = [self._make_account()]
        result = read.apply_transactions(accounts, [])
        
        self.assertEqual(len(result), 1,
                         "No transactions should leave accounts untouched.")
        self.assertEqual(result[0]['balance'], 1000.0)

    # D1 - Transaction code 01 (withdrawal)
    def test_D1_withdrawal(self):
        accounts = [self._make_account(balance = 1000.0, txns = 0)]
        txns = [self._make_transactions(code = "01", funds = 200.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['balance'], 799.95,
                         "Withdrawal should reduce balance by the amount withdrawn.")
        self.assertEqual(result[0]['total_transactions'], 1)

    # D2 - Transaction code 02 (pay bill)
    def test_D2_pay_bills(self):
        accounts = [self._make_account(balance = 500.0)]
        txns = [self._make_transactions(code = "02", funds = 50.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['balance'], 450.0,)
        self.assertEqual(result[0]['total_transactions'], 1)

    # D3 - Transaction code 03 (transfer)
    def test_D3_transfer_out(self):
        accounts = [self._make_account(balance = 300.0)]
        txns = [self._make_transactions(code = "03", funds = 75.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['balance'], 225.0,)
        self.assertEqual(result[0]['total_transactions'], 1)

    # D4 - Transaction code 04 (deposit)
    def test_D4_deposit(self):
        
        accounts = [self._make_account(balance = 200.0, txns = 0)]
        txns = [self._make_transactions(code = "04", funds = 150.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['balance'], 350.0,
                         "Deposit should increase the balance")
        self.assertEqual(result[0]['total_transactions'], 1)

    # D5 - Transaction code 05 (create)
    def test_D5_create_account(self):
        accounts = [self._make_account(num="11111")]
        txns = [self._make_transactions(code = "05", acct = "22222", funds = 0.0, name = "New Person")]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(len(result), 2,
                         "Create should Add a new account to the list.")
        self.assertEqual(result[1]['account_number'], '22222')
        self.assertEqual(result[1]['name'], 'New Person')
        self.assertEqual(result[1]['status'], 'A')

    # D6 - Transaction code 06 (delete)
    def test_D6_deleted_account(self):
        
        accounts = [
            self._make_account(num="11111"),
            self._make_account(num="22222", name = "To Delete")
        ]
        
        txns = [self._make_transactions(code = "06", acct = "22222")]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(len(result), 1,
                         "Delete should remove the account from the list.")
        self.assertEqual(result[0]['account_number'], '11111')

    # D7 - Transaction code 07 (disable)
    def test_D7_disable_account(self):
        accounts = [self._make_account(status="A")]
        txns = [self._make_transactions(code = "07")]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['status'], 'D',
                         "Disable account should set status to 'D'.")
        self.assertEqual(result[0]['balance'], 1000.0)

    # D8 - Transaction code 08 (change plan)
    def test_D8_change_plan(self):
        accounts = [self._make_account(plan = 'SP', txns = 0)]
        txns = [self._make_transactions(code="08")]

        result = read.apply_transactions(accounts, txns)

        self.assertEqual(result[0]['plan'], 'NP',
                         "Change-plan should update the plan to 'NP'")
        self.assertEqual(result[0]['total_transactions'], 1)

    # D9 - test unknown transaction code
    def test_D9_unknown_transaction_code(self):
        accounts = [self._make_account(balance = 1000.0)]
        txns = [self._make_transactions(code = "99")]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertAlmostEqual(result[0]['balance'], 1000.0,
                               msg= "An unknown transaction should not change balance.")

    # D10 - Two transactions (outer loops runs more than once)
    def test_D10_multiple_transactions(self):
        accounts = [self._make_account(balance = 1000.0, txns = 0)]
        txns = [
            self._make_transactions(code = "04", funds = 500.0),
            self._make_transactions(code = "01", funds = 200.0),
        ]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(result[0]['balance'], 1299.95,
                         "Two sequential transactions should both be applied.")
        self.assertEqual(result[0]['total_transactions'], 2)

    # D11 - Transaction account number not found 
    def test_D11_account_not_found(self):
        accounts = [self._make_account(num = "12345", balance = 1000.0)]
        txns = [self._make_transactions(code = "01", acct = "99999", funds = 200.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertAlmostEqual(result[0]['balance'], 1000.0,
                               msg= "If the account doesn't exist, nothing should happen.")
    
# =======================================================================================================================
# ADDITIONAL TESTS
# =======================================================================================================================

class TestAdditional(unittest.TestCase):
    
    #Helper functions for making account and transaction dicts
    def _make_account(self, num = "12345", name = "Test User", status = "A", balance = 1000.0, txns = 0, plan = "SP"):
        
        return {
            "account_number": num,
            "name": name,
            "status": status,
            "balance": balance,
            "total_transactions": txns,
            "plan": plan
        }
    
    def _make_transactions(self, code, acct = "12345", funds = 100.0, name = "Test User"):
        return {
            'transaction_code': code,
            'account_number': acct,
            'funds_involved': funds,
            'name': name,
        }

    # A1 - negative balance transaction 
    def test_A1_negative_balance(self):
        accounts = [self._make_account(balance = 100.0, plan = "SP")]
        txns = [self._make_transactions(code = "01", funds = 200.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        
        self.assertGreaterEqual(
            result[0]['balance'], 0.0,
            msg= (
                "BUG: Overdraft not prevented."
                f"Balance is {result[0]['balance']:.2f} after withdrawal "
                f"of 200.00 from account with 100.00"
            )
        )

    # A2 - create the same account number twice
    def test_A2_test_duplicate_account_creation(self):
        accounts = [self._make_account(num="12345", name="Original Owner")]
        txns = [self._make_transactions('05', acct="12345", funds=500.0,
                                       name="Impersonator")]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertEqual(
            len(result), 1,
            msg =(
                "BUG: Duplicate account created."
                f"Expected 1 account after rejecting duplicate create"
            )
        )

    # A2 - See if service fee is applied
    def test_A3_service_fee(self):
        accounts = [self._make_account(balance=1000.0, plan='SP')]
        txns = [self._make_transactions('01', funds=100.0)]
        
        result = read.apply_transactions(accounts, txns)
        
        self.assertAlmostEqual(
            result[0]['balance'], 899.95, places = 2,
            msg= (
                "BUG: Service fee applied."
                f"Expected 899.95 but got {result[0]['balance']:.2f}"
            )
        )
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
        