class InsufficientFundsException(Exception):
    def __init__(self, account_number, amount, balance):
        self.account_number = account_number
        self.amount = amount
        self.balance = balance
        super().__init__(
            f"Account {account_number}: Insufficient funds. "
            f"Requested: ${amount}, Available: ${balance}"
        )


class NegativeAmountException(Exception):
    def __init__(self, amount):
        self.amount = amount
        super().__init__(f"Invalid amount: ${amount}. Amount must be positive.")


class ZeroAmountException(Exception):
    def __init__(self):
        super().__init__("Transaction amount cannot be zero.")


class DailyLimitExceededException(Exception):
    def __init__(self, account_number, amount, remaining_limit):
        self.account_number = account_number
        self.amount = amount
        self.remaining_limit = remaining_limit
        super().__init__(
            f"Account {account_number}: Daily limit exceeded. "
            f"Requested: ${amount}, Remaining limit: ${remaining_limit}"
        )


class AccountNotFoundException(Exception):
    def __init__(self, account_number):
        self.account_number = account_number
        super().__init__(f"Account {account_number} not found in the system.")


class InvalidAccountTypeException(Exception):
    def __init__(self, account_number, account_type):
        self.account_number = account_number
        self.account_type = account_type
        super().__init__(
            f"Account {account_number} is a {account_type} account. "
            f"This operation is not allowed."
        )


# =========================
# Account Class
# =========================

class Account:
    def __init__(self, number, holder, balance, acc_type, daily_limit):
        self.number = number
        self.holder = holder
        self.balance = balance
        self.type = acc_type
        self.daily_limit = daily_limit
        self.total_withdrawn_today = 0.0
        self.withdraw_count = 0


# =========================
# Bank System
# =========================

class BankSystem:
    def __init__(self):
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.number] = account

    def get_account(self, account_number):
        if account_number not in self.accounts:
            raise AccountNotFoundException(account_number)
        return self.accounts[account_number]

    # -------------------------
    # Deposit
    # -------------------------
    def deposit(self, account_number, amount):
        if amount < 0:
            raise NegativeAmountException(amount)
        if amount == 0:
            raise ZeroAmountException()

        account = self.get_account(account_number)
        account.balance += amount
        print(f"Deposited ${amount} into {account_number}")

    # -------------------------
    # Withdraw
    # -------------------------
    def withdraw(self, account_number, amount):
        if amount < 0:
            raise NegativeAmountException(amount)
        if amount == 0:
            raise ZeroAmountException()

        account = self.get_account(account_number)

        if account.type == "Savings" and account.withdraw_count >= 3:
            raise InvalidAccountTypeException(account.number, account.type)

        if account.balance < amount:
            raise InsufficientFundsException(account.number, amount, account.balance)

        if account.total_withdrawn_today + amount > account.daily_limit:
            remaining = account.daily_limit - account.total_withdrawn_today
            raise DailyLimitExceededException(account.number, amount, remaining)

        account.balance -= amount
        account.total_withdrawn_today += amount
        account.withdraw_count += 1

        print(f"Withdrew ${amount} from {account_number}")

    # -------------------------
    # Transfer
    # -------------------------
    def transfer(self, from_account, to_account, amount):
        if amount < 0:
            raise NegativeAmountException(amount)
        if amount == 0:
            raise ZeroAmountException()

        sender = self.get_account(from_account)
        receiver = self.get_account(to_account)

        if sender.balance < amount:
            raise InsufficientFundsException(sender.number, amount, sender.balance)

        if sender.total_withdrawn_today + amount > sender.daily_limit:
            remaining = sender.daily_limit - sender.total_withdrawn_today
            raise DailyLimitExceededException(sender.number, amount, remaining)

        sender.balance -= amount
        receiver.balance += amount
        sender.total_withdrawn_today += amount

        print(f"Transferred ${amount} from {from_account} to {to_account}")

    # -------------------------
    # Check Balance
    # -------------------------
    def check_balance(self, account_number):
        account = self.get_account(account_number)
        print(f"Account {account_number} balance: ${account.balance}")
        return account.balance


# =========================
# Initial Test Accounts
# =========================

bank = BankSystem()

bank.add_account(Account("ACC001", "John Doe", 5000.0, "Savings", 1000.0))
bank.add_account(Account("ACC002", "Jane Smith", 15000.0, "Checking", 5000.0))
bank.add_account(Account("ACC003", "Bob Wilson", 500.0, "Savings", 500.0))


# =========================
# Test Scenarios
# =========================

tests = [
    lambda: bank.deposit("ACC001", 500),
    lambda: bank.deposit("ACC001", -100),
    lambda: bank.withdraw("ACC002", 0),
    lambda: bank.withdraw("ACC003", 600),
    lambda: bank.withdraw("ACC001", 800),
    lambda: bank.withdraw("ACC001", 500),
    lambda: bank.withdraw("ACC999", 100),
    lambda: bank.transfer("ACC002", "ACC001", 200),
    lambda: bank.transfer("ACC001", "ACC002", 2000),
]

for i, test in enumerate(tests, 1):
    try:
        print(f"\nTest {i}:")
        test()
    except Exception as e:
        print("❌ Exception:", e)