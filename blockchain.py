"""
Blockchain module for generating and verifying blockchains.
Implements block generation, SHA-256 hashing, and chain verification.
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
import random


@dataclass
class Transaction:
    """Represents a transaction in the blockchain."""
    sender: str
    receiver: str
    amount: float
    transaction_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return asdict(self)


@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: float
    transactions: List[Transaction]
    previous_hash: str
    data_hash: str
    block_hash: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'previous_hash': self.previous_hash,
            'data_hash': self.data_hash,
            'block_hash': self.block_hash
        }


class Blockchain:
    """Blockchain implementation with generation and verification capabilities."""

    def __init__(self):
        """Initialize an empty blockchain."""
        self.chain: List[Block] = []

    def generate_chain(self, num_blocks: int, transactions_per_block: int, seed: int = 7) -> List[Block]:
        """
        Generate a blockchain with the specified number of blocks.

        Args:
            num_blocks: Number of blocks to generate
            transactions_per_block: Number of transactions per block
            seed: Random seed for reproducibility

        Returns:
            List of Block objects
        """
        random.seed(seed)
        self.chain = []

        # Generate genesis block
        genesis_block = self._create_genesis_block(transactions_per_block)
        self.chain.append(genesis_block)

        # Generate subsequent blocks
        for i in range(1, num_blocks):
            previous_block = self.chain[-1]
            new_block = self._create_block(
                i,
                previous_block.block_hash,
                transactions_per_block
            )
            self.chain.append(new_block)

        return self.chain

    def _create_genesis_block(self, transactions_per_block: int) -> Block:
        """Create the genesis block (first block)."""
        transactions = self._generate_transactions(transactions_per_block, 0)
        data_hash = self.hash_transactions(transactions)
        block_hash = self.calculate_block_hash(0, 0.0, data_hash, "0" * 64)

        return Block(
            index=0,
            timestamp=0.0,
            transactions=transactions,
            previous_hash="0" * 64,
            data_hash=data_hash,
            block_hash=block_hash
        )

    def _create_block(self, index: int, previous_hash: str, transactions_per_block: int) -> Block:
        """Create a new block linked to the previous block."""
        timestamp = random.uniform(1000000000, 2000000000)
        transactions = self._generate_transactions(transactions_per_block, index)
        data_hash = self.hash_transactions(transactions)
        block_hash = self.calculate_block_hash(index, timestamp, data_hash, previous_hash)

        return Block(
            index=index,
            timestamp=timestamp,
            transactions=transactions,
            previous_hash=previous_hash,
            data_hash=data_hash,
            block_hash=block_hash
        )

    def _generate_transactions(self, count: int, block_index: int) -> List[Transaction]:
        """Generate random transactions for a block."""
        transactions = []
        accounts = [f"Account_{i}" for i in range(1, 11)]  # 10 accounts

        for i in range(count):
            sender = random.choice(accounts)
            receiver = random.choice([acc for acc in accounts if acc != sender])
            amount = round(random.uniform(1, 100), 2)
            tx_id = f"tx_{block_index}_{i}"

            transactions.append(Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount,
                transaction_id=tx_id
            ))

        return transactions

    @staticmethod
    def hash_transactions(transactions: List[Transaction]) -> str:
        """
        Calculate SHA-256 hash of transaction data.

        Args:
            transactions: List of Transaction objects

        Returns:
            Hexadecimal hash string
        """
        tx_data = json.dumps([tx.to_dict() for tx in transactions], sort_keys=True)
        return hashlib.sha256(tx_data.encode()).hexdigest()

    @staticmethod
    def calculate_block_hash(index: int, timestamp: float, data_hash: str, previous_hash: str) -> str:
        """
        Calculate SHA-256 hash of block header fields.

        Args:
            index: Block index
            timestamp: Block timestamp
            data_hash: Hash of transaction data
            previous_hash: Hash of previous block

        Returns:
            Hexadecimal hash string
        """
        block_header = f"{index}{timestamp}{data_hash}{previous_hash}"
        return hashlib.sha256(block_header.encode()).hexdigest()

    def verify_chain(self, chain: Optional[List[Block]] = None) -> Dict[str, Any]:
        """
        Verify the integrity of the blockchain.

        Args:
            chain: Blockchain to verify (uses self.chain if not provided)

        Returns:
            Dictionary with verification status and error details
        """
        if chain is None:
            chain = self.chain

        if not chain:
            return {
                'valid': False,
                'error': 'Blockchain is empty',
                'failed_block': None
            }

        # Verify genesis block
        genesis = chain[0]
        if genesis.previous_hash != "0" * 64:
            return {
                'valid': False,
                'error': 'Genesis block has invalid previous hash',
                'failed_block': 0
            }

        # Verify each block
        for i in range(len(chain)):
            block = chain[i]

            # Recalculate data hash
            recalculated_data_hash = self.hash_transactions(block.transactions)
            if recalculated_data_hash != block.data_hash:
                return {
                    'valid': False,
                    'error': f'Transaction data hash mismatch at block {i}',
                    'failed_block': i
                }

            # Recalculate block hash
            recalculated_block_hash = self.calculate_block_hash(
                block.index,
                block.timestamp,
                block.data_hash,
                block.previous_hash
            )
            if recalculated_block_hash != block.block_hash:
                return {
                    'valid': False,
                    'error': f'Block hash mismatch at block {i}',
                    'failed_block': i
                }

            # Verify previous hash link (except for genesis)
            if i > 0:
                if block.previous_hash != chain[i - 1].block_hash:
                    return {
                        'valid': False,
                        'error': f'Previous hash link broken at block {i}',
                        'failed_block': i
                    }

        return {
            'valid': True,
            'error': None,
            'failed_block': None
        }

    def get_block_count(self) -> int:
        """Return the number of blocks in the chain."""
        return len(self.chain)

    def get_transaction_count(self) -> int:
        """Return the total number of transactions in the chain."""
        return sum(len(block.transactions) for block in self.chain)

    def get_block_hashes(self) -> List[str]:
        """Return list of all block hashes."""
        return [block.block_hash for block in self.chain]
