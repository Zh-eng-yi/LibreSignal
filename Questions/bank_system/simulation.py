"""
All your implementation code for the bank system simulation goes here.
"""

import math

class Simulation:
    class Account:
        payment_id = 0

        class Cashback:
            def __init__(self, payment_id, amount, timestamp):
                self.payment_id = payment_id
                self.amount = amount
                self.timestamp = timestamp
        class Transaction:
            def __init__(self, timestamp, amount=0):
                self.amount = amount
                self.timestamp = timestamp

        def __init__(self, timestamp):
            self.transactions = [self.Transaction(timestamp)]
            self.total_outgoing = 0
            self.cashback = []
            self.current_payment = 0

        def refund(self, timestamp):
            while self.current_payment < len(self.cashback):
                c = self.cashback[self.current_payment]
                if c.timestamp <= timestamp:
                    self.transactions.append(self.Transaction(c.timestamp, c.amount))
                    self.current_payment += 1
                else:
                    break
            
        def deposit(self, timestamp, amount):
            self.refund(timestamp)
            self.transactions.append(self.Transaction(timestamp, amount))
            return self.get_balance(timestamp=timestamp, time_at=timestamp)

        def withdraw(self, timestamp, amount):
            self.refund(timestamp)
            balance_before = self.get_balance(timestamp=timestamp, time_at=timestamp)
            if balance_before >= amount:
                self.transactions.append(self.Transaction(timestamp, -amount))
                cashback = math.floor(amount * 0.02)
                refund_timestamp = timestamp + 86400000
                self.payment_id += 1
                self.cashback.append(self.Cashback(f'payment{self.payment_id}', cashback, refund_timestamp))
                return balance_before - amount
            else:
                return None

        def get_balance(self, timestamp, time_at):
            self.refund(timestamp)
            if self.transactions[0].timestamp > time_at:
                return None
            balance = 0
            for t in self.transactions:
                if t.timestamp <= time_at:
                    balance += t.amount
                else:
                    break
            return balance

        def get_total_outgoing(self, timestamp):
            total_outgoing = 0
            for t in self.transactions:
                if t.timestamp <= timestamp:
                    if t.amount < 0:
                        total_outgoing -= t.amount
                else:
                    break
            return total_outgoing

    def __init__(self):
        self.accounts = {}
        self.payment_counter = 1

    def create_account(self, timestamp: int, account_id: str) -> bool | None:
        if account_id in self.accounts:
            return False
        else:
            self.accounts[account_id] = self.Account(timestamp)
            return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        balance = account.deposit(timestamp, amount)
        return balance

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        if source_account_id not in self.accounts:
            return None
        if target_account_id not in self.accounts:
            return None
        if source_account_id == target_account_id:
            return None
        source_account = self.accounts[source_account_id]
        source_balance = source_account.withdraw(timestamp, amount)
        if source_balance is None:
            return None
        target_account = self.accounts[target_account_id]
        target_account.deposit(timestamp, amount)
        return source_balance

    def top_spenders(self, timestamp: int, n: int) -> list[str] | None:
        top_n_spenders = []
        for account_id in self.accounts:
            account = self.accounts[account_id]
            top_n_spenders.append((account_id, account.get_total_outgoing(timestamp)))
        top_n_spenders.sort(key=lambda x: (-x[1], x[0]))
        output = []
        for i in range(min(len(top_n_spenders), n)):
            output.append(f'{top_n_spenders[i][0]}({top_n_spenders[i][1]})')
        return output

    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        balance = account.withdraw(timestamp, amount)
        if balance is None:
            return None
        return f'payment{account.payment_id}'

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        for c in account.cashback:
            if c.payment_id == payment:
                if c.timestamp <= timestamp:
                    return 'CASHBACK_RECEIVED'
                else:
                    return 'IN_PROGRESS'
        return None

    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool | None:
        if account_id_1 == account_id_2:
            return False
        if account_id_1 not in self.accounts:
            return False
        if account_id_2 not in self.accounts:
            return False
        account_1 = self.accounts[account_id_1]
        account_2 = self.accounts[account_id_2]
        account_1.transactions.extend(account_2.transactions)
        account_1.transactions.sort(key=lambda t: t.timestamp)
        account_1.cashback.extend(account_2.cashback)
        account_1.cashback.sort(key=lambda c: c.timestamp)
        account_1.current_payment += account_2.current_payment
        account_1.refund(timestamp)
        self.accounts.pop(account_2, None)
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        if account_id not in self.accounts:
            return None
        account = self.accounts[account_id]
        return account.get_balance(timestamp, time_at)