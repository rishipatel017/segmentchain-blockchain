"""
State machine module for simulating ledger state transitions.
Implements balance updates and checkpoint recording at segment boundaries.
"""

from typing import Dict, List, Any
from blockchain import Block, Transaction


class StateMachine:
    """Simulates a simple ledger with account balances."""

    def __init__(self, initial_balances: Dict[str, float] = None):
        """
        Initialize the state machine.

        Args:
            initial_balances: Starting balances for accounts (default: 1000 each)
        """
        if initial_balances is None:
            # Default: 10 accounts with 1000 each
            self.balances = {f"Account_{i}": 1000.0 for i in range(1, 11)}
        else:
            self.balances = initial_balances.copy()

        self.checkpoints: Dict[int, Dict[str, float]] = {}

    def derive_state(self, blocks: List[Block], segment_boundaries: List[int] = None) -> Dict[str, Any]:
        """
        Process blocks in order and update balances.

        Args:
            blocks: List of blocks to process
            segment_boundaries: Block indices where to record checkpoints

        Returns:
            Dictionary with latest state and checkpoints
        """
        # Reset to initial state
        if segment_boundaries is None:
            segment_boundaries = []

        self.checkpoints = {}

        # Process each block
        for block in blocks:
            # Process transactions in order
            for tx in block.transactions:
                self._process_transaction(tx)

            # Record checkpoint if this is a segment boundary
            if block.index in segment_boundaries:
                self.checkpoints[block.index] = self.balances.copy()

        return {
            'latest_state': self.balances.copy(),
            'checkpoints': self.checkpoints.copy()
        }

    def _process_transaction(self, transaction: Transaction) -> None:
        """
        Process a single transaction and update balances.

        Args:
            transaction: Transaction to process
        """
        # Deduct from sender
        if transaction.sender in self.balances:
            self.balances[transaction.sender] -= transaction.amount

        # Add to receiver
        if transaction.receiver in self.balances:
            self.balances[transaction.receiver] += transaction.amount

    def get_balances(self) -> Dict[str, float]:
        """Return current account balances."""
        return self.balances.copy()

    def get_checkpoint(self, block_index: int) -> Dict[str, float]:
        """
        Get the state checkpoint at a specific block index.

        Args:
            block_index: Block index to retrieve checkpoint for

        Returns:
            Account balances at that checkpoint, or None if not found
        """
        return self.checkpoints.get(block_index)

    def get_all_checkpoints(self) -> Dict[int, Dict[str, float]]:
        """Return all recorded checkpoints."""
        return self.checkpoints.copy()

    def validate_balances(self) -> bool:
        """
        Validate that all balances are non-negative.

        Returns:
            True if all balances are valid, False otherwise
        """
        return all(balance >= 0 for balance in self.balances.values())

    def get_total_balance(self) -> float:
        """Return the sum of all account balances."""
        return sum(self.balances.values())
