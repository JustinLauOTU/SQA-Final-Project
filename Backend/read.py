import print_error

STUDENT_FEE = 0.05
NON_STUDENT_FEE = 0.10

def read_old_bank_accounts(file_path):
    """
    Reads and validates the bank account file format with plan type (SP/NP)
    Returns list of accounts and prints fatal errors for invalid format
    """
    accounts = []
    with open(file_path, 'r') as file:
        for line_num, line in enumerate(file, 1):
            clean_line = line.rstrip('\n')
            
            # Validate line length (now 44 chars to include plan type)
            if len(clean_line) != 45:
                print(f"ERROR: Fatal error - Line {line_num}: Invalid length ({len(clean_line)} chars, expected 45)")
                continue

            try:
                # Extract fields with positional validation
                account_number = clean_line[0:5]
                name = clean_line[6:25]  # 20 characters
                status = clean_line[27]
                balance_str = clean_line[29:37]  # 8 characters
                transactions_str = clean_line[38:42]  # 4 characters
                plan_type = clean_line[43:45]  # 2 characters (SP/NP)

                # Validate account number
                if not account_number.isdigit():
                    print(f"ERROR: Fatal error - Line {line_num}: Account number must be 5 digits")
                    continue

                # Validate status
                if status not in ('A', 'D'):
                    print(f"ERROR: Fatal error - Line {line_num}: Invalid status '{status}'. Must be 'A' or 'D'")
                    continue

                # Validate balance format with explicit negative check
                if balance_str[0] == '-':
                    print(f"ERROR: Fatal error - Line {line_num}: Negative balance detected: {balance_str}")
                    continue
                
                if (len(balance_str) != 8 or 
                    balance_str[5] != '.' or 
                    not balance_str[:5].isdigit() or 
                    not balance_str[6:].isdigit()):
                    print(f"ERROR: Fatal error - Line {line_num}: Invalid balance format. Expected XXXXX.XX, got {balance_str}")
                    continue

                # Validate transaction count
                if not transactions_str.isdigit():
                    print(f"ERROR: Fatal error - Line {line_num}: Transaction count must be 4 digits")
                    continue

                # Validate plan type
                if plan_type not in ('SP', 'NP'):
                    print(f"ERROR: Fatal error - Line {line_num}: Invalid plan type '{plan_type}'. Must be SP or NP")
                    continue

                # Convert values
                balance = float(balance_str)
                transactions = int(transactions_str)

                # Business rule validation
                if balance < 0:
                    print(f"ERROR: Fatal error - Line {line_num}: Negative balance detected")
                    continue
                if transactions < 0:
                    print(f"ERROR: Fatal error - Line {line_num}: Negative transaction not allowed")
                    continue

                accounts.append({
                    'account_number': account_number.lstrip('0') or '0',
                    'name': name.strip(),
                    'status': status,
                    'balance': balance,
                    'total_transactions': transactions,
                    'plan': plan_type
                })

            except Exception as e:
                print(f"ERROR: Fatal error - Line {line_num}: Unexpected error - {str(e)}")
                continue

    return accounts

#this function reads in the combined transaction file
def read_transactions(file_path):
    transactions = []
    with open(file_path, 'r') as file: #opens file
        for line_num, line in enumerate(file, 1):
            clean_line = line.rstrip('\n')

            #checks for correct line length
            if len(clean_line) != 41:
                print(f"ERROR: Fatal error - Line {line_num}: Invalid length ({len(clean_line)} chars, expected 41)")
                continue

            try: #gets each individual part of the line and saves them into variables
                transaction_code = clean_line[0:2]
                name = clean_line[3:23]
                account_number = clean_line[24:29]
                funds_involved = clean_line[30:38]
                
                transactions.append({ #adds to a list with correct formatting
                    'transaction_code': transaction_code,
                    'name': name.strip(),
                    'account_number': account_number.lstrip('0') or '0', #strips leading zeroes
                    'funds_involved': float(funds_involved.lstrip('0') or '0'), #strips leading zeroes
                })
            
            except Exception as e:
                print(f"ERROR: {e}")
                continue

    return transactions

#This function deducts the service fee for each transaction from an account based on plan type
def _deduct_service_fee(account, transaction_code, funds_involved):
    
    fee = STUDENT_FEE if account['plan'] == 'SP' else NON_STUDENT_FEE
    total_cost = funds_involved + fee
    if total_cost < account['balance']:
        account['balance'] = round(account['balance'] - (total_cost), 2)
    
    if account['balance'] < 0:
        print_error.log_constraint_error(
            f"Service fee on transaction {transaction_code} caused negative balance"
            f"on account {account['account_number']} (balance: {account['balance']:.2f})",
            "negative balance after fee"
        )
    
#this function applies the transactions to the accounts list
def apply_transactions(accounts, transactions):
    #goes through each transaction
    for x in transactions:
        match x['transaction_code']:
            case '01': #subtracts from account owners balance
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        _deduct_service_fee(y, x['transaction_code'], x['funds_involved'])
                        # y['balance'] -= x['funds_involved']
                        y['total_transactions'] += 1
                        break
            case '02': #subtracts from account owners balance
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        y['balance'] -= x['funds_involved']
                        y['total_transactions'] += 1
                        break
            case '03': #subtracts from account owners balance
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        y['balance'] -= x['funds_involved']
                        y['total_transactions'] += 1
                        break
            case '04': #adds to account owners balance
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        y['balance'] += x['funds_involved']
                        y['total_transactions'] += 1
                        break
            case '05': #creates a new account and adds it to the account list
                if any(y['account_number'] == x['account_number'] for y in accounts):
                    print(f"ERROR: account already exists")
                else:
                    accounts.append({
                        'account_number': x['account_number'],
                        'name': x['name'],
                        'status': 'A',
                        'balance': x['funds_involved'],
                        'total_transactions': 0,
                        'plan': 'SP'}
                    )
            case '06': #removes an account from the list
                index = None
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        index = accounts.index(y)
                        break
                accounts.pop(index)
            case '07': #changes the account status to disabled
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        y['status'] = 'D'
                        break
            case '08': #changes the plan type of the account to NP
                for y in accounts:
                    if y['account_number'] == x['account_number']:
                        y['plan'] = 'NP'
                        y['total_transactions'] += 1
                        break
    return accounts



