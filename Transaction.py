from decimal import Decimal

class Transaction:
    def __init__(self, transaction_code: str, holders_name: str, account_num: str, balance: Decimal, misc: str = ''):
        self.transaction_code = transaction_code
        self.holders_name = holders_name
        self.account_num = account_num
        self.balance = balance
        self.misc = misc

    @staticmethod
    def pad_left(line: str, width: int, pad_char: str = '0') -> str:
        """Right-justify a string by padding on the left."""
        return str(line).rjust(width, pad_char)

    @staticmethod
    def pad_right(line: str, width: int, pad_char: str = ' ') -> str:
        """Left-justify a string by padding on the right."""
        return str(line).ljust(width, pad_char)

    @staticmethod
    def format_amount(amount: Decimal) -> str:
        """Convert a Decimal amount to 8-character format (e.g. 150.40 = 00150.40)"""
        dollars = int(amount)
        cents = int((amount - dollars) * 100)
        return f"{dollars:05d}.{cents:02d}"

    def format(self):
        """Format this transaction into a 40-character daily transaction record"""
        code = self.pad_left(self.transaction_code, 2)
        name = self.pad_right(self.holders_name[:20], 20)
        account_number = self.pad_left(self.account_num, 5)
        amount = self.format_amount(self.balance)
        misc = self.pad_right(self.misc[:2], 2)
        return f"{code} {name} {account_number} {amount} {misc}"