"""
Unit tests for worldcar.utils module.
"""

import pytest
import networkx as nx

from worldcar.utils import (
    haversine_distance,
    validate_coordinates,
    validate_coordinate_pair,
    validate_graph,
    get_bounding_box,
    format_distance,
    format_coordinates,
    compute_path_total_length,
    meters_to_km,
    km_to_meters,
)


class TestDistanceCalculations:
    """Test distance calculation functions."""

    def test_haversine_distance_same_point(self):
        """Distance from a point to itself should be zero."""
        dist = haversine_distance(40.9856, 29.0298, 40.9856, 29.0298)
        assert abs(dist) < 1.0  # Less than 1 meter

    def test_haversine_distance_known_distance(self):
        """Test with approximate known distance (Moda to Fenerbahçe)."""
        # Approximate distance is ~2.5 km
        dist = haversine_distance(40.9856, 29.0298, 40.9638, 29.0408)
        assert 2000 < dist < 3000  # Between 2-3 km

    def test_haversine_distance_symmetry(self):
        """Distance should be symmetric (A to B == B to A)."""
        dist1 = haversine_distance(40.9856, 29.0298, 40.9638, 29.0408)
        dist2 = haversine_distance(40.9638, 29.0408, 40.9856, 29.0298)
        assert abs(dist1 - dist2) < 0.01  # Should be essentially equal


class TestCoordinateValidation:
    """Test coordinate validation functions."""

    def test_validate_coordinates_valid(self):
        """Valid coordinates should pass validation."""
        assert validate_coordinates(40.9856, 29.0298) is True
        assert validate_coordinates(0.0, 0.0) is True
        assert validate_coordinates(-45.5, 120.3) is True

    def test_validate_coordinates_invalid_latitude(self):
        """Invalid latitude should fail validation."""
        assert validate_coordinates(91.0, 29.0) is False
        assert validate_coordinates(-91.0, 29.0) is False

    def test_validate_coordinates_invalid_longitude(self):
        """Invalid longitude should fail validation."""
        assert validate_coordinates(40.0, 181.0) is False
        assert validate_coordinates(40.0, -181.0) is False

    def test_validate_coordinates_nan(self):
        """NaN coordinates should fail validation."""
        assert validate_coordinates(float('nan'), 29.0) is False
        assert validate_coordinates(40.0, float('nan')) is False

    def test_validate_coordinates_inf(self):
        """Infinite coordinates should fail validation."""
        assert validate_coordinates(float('inf'), 29.0) is False
        assert validate_coordinates(40.0, float('-inf')) is False

    def test_validate_coordinate_pair_valid(self):
        """Valid coordinate pair should pass validation."""
        origin = (40.9856, 29.0298)
        dest = (40.9638, 29.0408)
        is_valid, error = validate_coordinate_pair(origin, dest)
        assert is_valid is True
        assert error is None

    def test_validate_coordinate_pair_same_location(self):
        """Same origin and destination should fail."""
        origin = (40.9856, 29.0298)
        dest = (40.9856, 29.0298)
        is_valid, error = validate_coordinate_pair(origin, dest)
        assert is_valid is False
        assert "same" in error.lower()


class TestGraphValidation:
    """Test graph validation functions."""

    def test_validate_graph_valid(self):
        """Valid graph should pass validation."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.9856, x=29.0298)
        G.add_node(2, y=40.9638, x=29.0408)
        G.add_edge(1, 2, length=1000)

        is_valid, error = validate_graph(G)
        assert is_valid is True
        assert error is None

    def test_validate_graph_empty(self):
        """Empty graph should fail validation."""
        G = nx.MultiDiGraph()
        is_valid, error = validate_graph(G)
        assert is_valid is False
        assert "no nodes" in error.lower()

    def test_validate_graph_missing_coordinates(self):
        """Graph with nodes missing coordinates should fail."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.9856)  # Missing 'x'
        G.add_node(2, y=40.9638, x=29.0408)
        G.add_edge(1, 2, length=1000)

        is_valid, error = validate_graph(G)
        assert is_valid is False
        assert "coordinate" in error.lower()

    def test_validate_graph_missing_edge_length(self):
        """Graph with edges missing length should fail."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.9856, x=29.0298)
        G.add_node(2, y=40.9638, x=29.0408)
        G.add_edge(1, 2)  # Missing 'length'

        is_valid, error = validate_graph(G)
        assert is_valid is False
        assert "length" in error.lower()


class TestGraphAnalysis:
    """Test graph analysis functions."""

    def test_get_bounding_box(self):
        """Test bounding box calculation."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.0, x=29.0)
        G.add_node(2, y=41.0, x=30.0)
        G.add_node(3, y=40.5, x=29.5)

        bbox = get_bounding_box(G)

        assert bbox['north'] == 41.0
        assert bbox['south'] == 40.0
        assert bbox['east'] == 30.0
        assert bbox['west'] == 29.0


class TestFormatting:
    """Test formatting functions."""

    def test_format_distance_meters(self):
        """Test distance formatting in meters."""
        assert "500.00 m" in format_distance(500)

    def test_format_distance_kilometers(self):
        """Test distance formatting in kilometers."""
        result = format_distance(1500)
        assert "1.50 km" in result or "1.5 km" in result

    def test_format_coordinates(self):
        """Test coordinate formatting."""
        result = format_coordinates(40.9856, 29.0298)
        assert "40.985600" in result
        assert "29.029800" in result

    def test_meters_to_km(self):
        """Test meter to kilometer conversion."""
        assert meters_to_km(1000) == 1.0
        assert meters_to_km(2500) == 2.5

    def test_km_to_meters(self):
        """Test kilometer to meter conversion."""
        assert km_to_meters(1.0) == 1000.0
        assert km_to_meters(2.5) == 2500.0


class TestPathUtilities:
    """Test path utility functions."""

    def test_compute_path_total_length(self):
        """Test path length computation."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.0, x=29.0)
        G.add_node(2, y=40.1, x=29.1)
        G.add_node(3, y=40.2, x=29.2)
        G.add_edge(1, 2, length=1000)
        G.add_edge(2, 3, length=1500)

        path = [1, 2, 3]
        length = compute_path_total_length(G, path)

        assert length == 2500.0

    def test_compute_path_total_length_single_node(self):
        """Path with single node should have zero length."""
        G = nx.MultiDiGraph()
        G.add_node(1, y=40.0, x=29.0)

        path = [1]
        length = compute_path_total_length(G, path)

        assert length == 0.0
