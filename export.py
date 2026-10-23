"""
Export module for exporting experiment results.
Implements JSON and CSV export functionality.
"""

import json
import csv
from typing import Dict, Any, List
from datetime import datetime


class ExportManager:
    """Manager for exporting experiment results."""

    def __init__(self):
        """Initialize the export manager."""
        pass

    def export_results_json(
        self,
        configuration: Dict[str, Any],
        results: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Export experiment results as JSON.

        Args:
            configuration: Simulation configuration
            results: Experiment results
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"segmentchain_experiment_{timestamp}.json"

        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'simulation_only': True,
            'assumptions': 'This is a simulated blockchain for educational purposes',
            'configuration': configuration,
            'results': results
        }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        return filename

    def export_table_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str = None,
        table_name: str = "data"
    ) -> str:
        """
        Export tabular data as CSV.

        Args:
            data: List of dictionaries to export
            filename: Output filename (auto-generated if not provided)
            table_name: Name of the table (for filename generation)

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"segmentchain_{table_name}_{timestamp}.csv"

        if not data:
            with open(filename, 'w') as f:
                f.write("# No data to export")
            return filename

        # Get headers from first row
        fieldnames = list(data[0].keys())

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

        return filename

    def export_node_assignment_csv(
        self,
        assignment_matrix: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        Export node assignment matrix as CSV.

        Args:
            assignment_matrix: Assignment matrix from AssignmentEngine
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        return self.export_table_csv(
            assignment_matrix,
            filename,
            "node_assignment"
        )

    def export_storage_metrics_csv(
        self,
        storage_data: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        Export storage metrics as CSV.

        Args:
            storage_data: Storage metrics data
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        return self.export_table_csv(
            storage_data,
            filename,
            "storage_metrics"
        )

    def export_segment_summary_csv(
        self,
        segment_summary: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        Export segment summary as CSV.

        Args:
            segment_summary: Segment summary data
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        return self.export_table_csv(
            segment_summary,
            filename,
            "segment_summary"
        )

    def export_availability_results_csv(
        self,
        availability_data: Dict[str, Any],
        filename: str = None
    ) -> str:
        """
        Export availability results as CSV.

        Args:
            availability_data: Availability results dictionary
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"segmentchain_availability_{timestamp}.csv"

        # Convert to flat structure for CSV
        flat_data = []

        # Add summary
        summary = {
            'metric': 'summary',
            'total_nodes': availability_data.get('total_nodes', ''),
            'online_nodes': availability_data.get('online_nodes', ''),
            'offline_nodes': availability_data.get('offline_nodes', ''),
            'total_segments': availability_data.get('total_segments', ''),
            'available_segments': availability_data.get('available_segments', ''),
            'availability_percentage': availability_data.get('availability_percentage', '')
        }
        flat_data.append(summary)

        # Add surviving replicas per segment
        surviving_replicas = availability_data.get('surviving_replicas', {})
        for segment_id, count in surviving_replicas.items():
            flat_data.append({
                'metric': 'segment_replicas',
                'segment_id': segment_id,
                'surviving_replicas': count
            })

        # Add failed nodes
        failed_nodes = availability_data.get('failed_node_ids', [])
        for node_id in failed_nodes:
            flat_data.append({
                'metric': 'failed_node',
                'node_id': node_id
            })

        return self.export_table_csv(
            flat_data,
            filename,
            "availability"
        )

    def export_probability_results_csv(
        self,
        probability_data: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """
        Export probability analysis results as CSV.

        Args:
            probability_data: Probability results data
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        return self.export_table_csv(
            probability_data,
            filename,
            "probability_analysis"
        )

    def create_experiment_report(
        self,
        configuration: Dict[str, Any],
        blockchain_info: Dict[str, Any],
        segmentation_info: Dict[str, Any],
        storage_comparison: Dict[str, Any],
        availability_info: Dict[str, Any] = None,
        filename: str = None
    ) -> str:
        """
        Create a comprehensive experiment report.

        Args:
            configuration: Simulation configuration
            blockchain_info: Blockchain information
            segmentation_info: Segmentation information
            storage_comparison: Storage comparison results
            availability_info: Availability results (optional)
            filename: Output filename (auto-generated if not provided)

        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"segmentchain_report_{timestamp}.json"

        report = {
            'export_timestamp': datetime.now().isoformat(),
            'simulation_only': True,
            'assumptions': 'This is a simulated blockchain for educational purposes',
            'configuration': configuration,
            'blockchain': blockchain_info,
            'segmentation': segmentation_info,
            'storage_comparison': storage_comparison
        }

        if availability_info is not None:
            report['availability'] = availability_info

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return filename
