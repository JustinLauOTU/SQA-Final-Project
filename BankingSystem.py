import sys
from decimal import Decimal

from AccountsManager import AccountsManager
from FileHandler import FileHandler
from Session import Session
from TransactionLog import TransactionLog
from TransactionProcessor import TransactionProcessor
from UserInterface import UserInterface


class BankingSystem:
    """
    Main application controller for banking system front end functionality. Will be the one to arrange the login/logout,
    display menus, user commands, and delegates transaction processing to TransactionProcessor.
    """

    # For mapping transaction command strings to the corresponding handler method names
    COMMAND_HANDLERS = {
        'logout': '_process_logout',
        'withdrawal': '_handle_withdrawal',
        'transfer': '_handle_transfer',
        'paybill': '_handle_paybill',
        'deposit': '_handle_deposit',
        'create': '_handle_create',
        'delete': '_handle_delete',
        'disable': '_handle_disable',
        'changeplan': '_handle_changeplan',
    }

    def __init__(self, current_accounts_file, transaction_output_file):
        """
        Initialise the banking system and file paths.

        :param current_accounts_file: Path to current bank accounts file
        :param transaction_output_file: Path to output transaction file
        """
        self.session = Session()
        self.account_manager = AccountsManager()
        self.log = TransactionLog()
        self.file_handler = FileHandler()
        self.ui = UserInterface()
        self.transaction_processor = TransactionProcessor(self.account_manager, self.session, self.log)
        self.current_accounts_file = current_accounts_file
        self.daily_transaction_file = transaction_output_file

    def run(self):
        """
        Main execution loop. Attempts login first; if successful, repeatedly displays the menu, reads a command, and
        dispatches it to the appropriate handler.
        """
        if self._process_login():
            while True:
                # self.ui.display_menu(self.session.is_admin())
                cmd = self.ui.prompt_transaction_type(self.session.is_admin())
                if cmd == "logout":
                    self._process_logout()
                    break
                elif not self.session.can_execute(cmd):
                    self.ui.display_error("Invalid command")
                else:
                    getattr(self, self.COMMAND_HANDLERS[cmd])()

    def _check_login(self) -> bool:
        """
        Verify that the user is NOT already logged in. Displays an error and returns False if already logged in.

        :return: True if not logged in (good to proceed), False if already logged in.
        """
        if self.session.is_logged_in():
            self.ui.display_error("Already logged in")
            return False
        return True

    def _process_login(self):
        """
        Handle Login sequence:
            - Prompt user for mode and account (if standard)
            - Load accounts file
            - Validate the account exists for standard mode
            - create session if all is good
        :return: True if login succeeded, False otherwise.
        """

        # Prevent double login
        if not self._check_login():
            return False

        mode, user = self.ui.prompt_login()

        # Load accounts from file; error if file cannot be read
        if not self.account_manager.load_accounts(self.current_accounts_file):
            self.ui.display_error("Failed to load accounts. Please try again.")
            return False

        # For standard mode, check that the account holder exists
        if mode == 'standard':
            account = self.account_manager.find_account_by_name(user)
            if not account:
                self.ui.display_error(f"Account not found")
                return False

        # All checks are good - login
        self.session.login(mode, user)

        return True

    def _process_logout(self):
        """
        Handle logout:
        - Write the daily transaction file.
        - Clear the transaction log.
        - End the session.
        """
        if self.session.is_logged_in():
            self.log.write_session_file(self.daily_transaction_file)
            self.log.clear()
            self.session.logout()
            self.ui.display_success(f"Logout successful")


    def _handle_account_name(self) -> str:
        if self.session.is_admin():
            account_holder = self.ui.prompt_account_name()
        else:
            account_holder = self.session.current_user
        return account_holder

    # =========================TRANSACTION HANDLERS=========================

    def _handle_withdrawal(self):
        """Get withdrawal input and call transaction_processor.withdrawal()."""

        # Getting account_holder name
        account_holder = self._handle_account_name()
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.withdrawal(account_holder, account_number, amount)

    def _handle_transfer(self):
        """Get transfer input and call transaction_processor.transfer()."""
        account_holder = self._handle_account_name()
        from_account = self.ui.prompt_account_number()
        to_account = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.transfer(from_account, to_account, amount)

    def _handle_paybill(self):
        """Get paybill input and call transaction_processor.paybill()."""
        account_holder = self._handle_account_name()
        account_number = self.ui.prompt_account_number()
        company = self.ui.prompt_company_code()
        amount = self.ui.prompt_amount()
        self.transaction_processor.paybill(account_number, company, amount)

    def _handle_deposit(self):
        """Get deposit input and call transaction_processor.deposit()."""
        account_holder = self._handle_account_name()
        account_number = self.ui.prompt_account_number()
        amount = self.ui.prompt_amount()
        self.transaction_processor.deposit(account_holder, account_number, amount)

    def _handle_create(self):
        """Get create input and call transaction_processor.create()."""
        account_holder = self.ui.prompt_account_name()
        amount = self.ui.prompt_amount()

        # Constraint for account creation: initial balance cannot exceed 99999.99
        if amount > Decimal(99999.99):
            self.ui.display_error("Invalid amount")
            return
        self.transaction_processor.create(account_holder, amount)

    def _handle_delete(self):
        """Get delete input and call transaction_processor.delete()."""
        account_holder = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.delete(account_holder, account_number)

    def _handle_disable(self):
        """Get disable input and call transaction_processor.disable()."""
        account_holder = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.disable(account_holder, account_number)

    def _handle_changeplan(self):
        """Get changeplan input and call transaction_processor.changeplan()."""
        account_holder = self.ui.prompt_account_name()
        account_number = self.ui.prompt_account_number()
        self.transaction_processor.change_plan(account_number)

def main():
    """
    Create BankingSystem and run.
    Accepts command line arguments: current_accounts_file transaction_output_file
    Usage: python BankingSystem.py current_accounts.txt transaction_output.atf
    """
    if len(sys.argv) != 3:
        print("Usage: python BankingSystem.py <current_accounts_file> <transaction_output_file>")
        print("Example: python BankingSystem.py current_bank_accounts.txt daily_transaction.atf")
        sys.exit(1)

    current_accounts_file = sys.argv[1]
    transaction_output_file = sys.argv[2]

    system = BankingSystem(current_accounts_file, transaction_output_file)
    system.run()

if __name__ == "__main__":
    main()
