import read
import write

def main():
    get_accounts = read.read_old_bank_accounts("Backend/master_bank_accounts.txt")
    print("old", get_accounts)
    
    get_transactions = read.read_transactions("Backend/daily_transaction.atf")
    new_accounts = read.apply_transactions(get_accounts, get_transactions)
    print("new", new_accounts)
    
    write.write_new_current_accounts(new_accounts, "Backend/new_master_bank_accounts.txt")

if __name__ == "__main__":
    main()
