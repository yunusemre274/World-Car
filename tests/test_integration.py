"""
Integration tests for WorldCar routing system.

These tests validate the complete workflow from graph loading to route computation.
Note: These tests may take longer to run as they involve downloading OSM data.
"""

import pytest
import networkx as nx

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


class TestCompleteWorkflow:
    """Test the complete routing workflow end-to-end."""

    @pytest.fixture(scope="class")
    def graph(self):
        """Load graph once for all tests in this class."""
        from worldcar.graph_loader import GraphLoader
        from worldcar.config import DEFAULT_LOCATION

        loader = GraphLoader(DEFAULT_LOCATION)
        G = loader.get_or_create_graph()

        # Validate graph was loaded
        assert G is not None
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0

        return G

    @pytest.fixture(scope="class")
    def node_mapper(self, graph):
        """Create node mapper for the graph."""
        from worldcar.node_mapper import NodeMapper

        mapper = NodeMapper(graph)
        assert mapper is not None
        return mapper

    @pytest.fixture(scope="class")
    def router(self, graph, node_mapper):
        """Create router with graph and mapper."""
        from worldcar.algorithms import Router

        router_obj = Router(graph, node_mapper)
        assert router_obj is not None
        return router_obj

    def test_graph_loading(self, graph):
        """Test that graph is loaded correctly."""
        # Check basic structure
        assert isinstance(graph, (nx.MultiDiGraph, nx.DiGraph))
        assert graph.number_of_nodes() > 1000  # Kadıköy should have many nodes
        assert graph.number_of_edges() > 1000

        # Check nodes have required attributes
        sample_node = list(graph.nodes(data=True))[0]
        node_id, data = sample_node
        assert 'x' in data
        assert 'y' in data

        # Check edges have required attributes
        sample_edge = list(graph.edges(data=True))[0]
        u, v, data = sample_edge
        assert 'length' in data

    def test_node_mapper_initialization(self, node_mapper):
        """Test that node mapper is initialized correctly."""
        stats = node_mapper.get_stats()
        assert stats['num_nodes'] > 0
        assert stats['kdtree_enabled'] is True

    def test_coordinate_mapping(self, node_mapper):
        """Test mapping coordinates to nodes."""
        # Use coordinates in Kadıköy
        lat, lon = 40.9856, 29.0298  # Moda

        node_id = node_mapper.find_nearest_node(lat, lon)
        assert node_id is not None

        # Get node coordinates back
        node_lat, node_lon = node_mapper.get_node_coordinates(node_id)
        assert isinstance(node_lat, float)
        assert isinstance(node_lon, float)

    def test_snap_to_network(self, node_mapper):
        """Test snapping coordinates to network."""
        lat, lon = 40.9856, 29.0298  # Moda

        result = node_mapper.snap_to_network(lat, lon)

        assert result['success'] is True
        assert result['node_id'] is not None
        assert result['node_lat'] is not None
        assert result['node_lon'] is not None
        assert result['distance'] is not None
        assert result['distance'] < 500  # Within max search radius

    def test_shortest_path_computation(self, router):
        """Test computing shortest path between two points."""
        # Moda to Fenerbahçe
        origin_lat, origin_lon = 40.9856, 29.0298
        dest_lat, dest_lon = 40.9638, 29.0408

        result = router.compute_shortest_path(
            origin_lat, origin_lon,
            dest_lat, dest_lon
        )

        # Check result structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'path' in result
        assert 'distance' in result

        # If route was found (depends on network connectivity)
        if result['success']:
            assert len(result['path']) > 0
            assert result['distance'] > 0
            assert len(result['nodes']) == len(result['path'])
            assert result['origin_node'] is not None
            assert result['dest_node'] is not None
        else:
            # Route failed - check error message exists
            assert 'message' in result
            assert len(result['message']) > 0

    def test_multiple_routes(self, router):
        """Test computing multiple routes."""
        routes = [
            ((40.9856, 29.0298), (40.9638, 29.0408)),  # Moda to Fenerbahçe
            ((40.9904, 29.0255), (40.9780, 29.0450)),  # Center to Bağdat Ave
        ]

        for origin, dest in routes:
            result = router.compute_shortest_path(
                origin[0], origin[1],
                dest[0], dest[1]
            )

            assert isinstance(result, dict)
            assert 'success' in result

            if result['success']:
                # Valid route
                assert len(result['path']) > 0
                assert result['distance'] > 0

    def test_invalid_coordinates(self, router):
        """Test handling of invalid coordinates."""
        # Invalid latitude
        result = router.compute_shortest_path(
            91.0, 29.0,  # Latitude > 90
            40.9638, 29.0408
        )

        assert result['success'] is False
        assert 'invalid' in result['message'].lower()

    def test_same_origin_destination(self, router):
        """Test handling when origin equals destination."""
        lat, lon = 40.9856, 29.0298

        result = router.compute_shortest_path(lat, lon, lat, lon)

        assert result['success'] is False
        assert 'same' in result['message'].lower()

    def test_graph_statistics(self, graph):
        """Test computing graph statistics."""
        from worldcar.statistics import compute_graph_statistics

        stats = compute_graph_statistics(graph)

        # Check all expected keys exist
        assert 'num_nodes' in stats
        assert 'num_edges' in stats
        assert 'total_length_m' in stats
        assert 'total_length_km' in stats
        assert 'avg_edge_length_m' in stats
        assert 'num_connected_components' in stats
        assert 'bounding_box' in stats

        # Check values are reasonable
        assert stats['num_nodes'] > 0
        assert stats['num_edges'] > 0
        assert stats['total_length_m'] > 0
        assert stats['total_length_km'] > 0

    def test_connectivity_analysis(self, graph):
        """Test connectivity analysis."""
        from worldcar.statistics import analyze_connectivity

        conn = analyze_connectivity(graph)

        assert 'is_connected' in conn
        assert 'num_components' in conn
        assert 'component_sizes' in conn
        assert 'largest_component_size' in conn

        # Kadıköy graph should be mostly connected
        if conn['num_components'] > 1:
            # If multiple components, largest should be dominant
            assert conn['largest_component_size'] > graph.number_of_nodes() * 0.8


class TestPerformance:
    """Test performance of routing operations."""

    @pytest.fixture(scope="class")
    def setup_router(self):
        """Set up router for performance tests."""
        from worldcar.graph_loader import GraphLoader
        from worldcar.node_mapper import NodeMapper
        from worldcar.algorithms import Router

        loader = GraphLoader()
        G = loader.get_or_create_graph()
        mapper = NodeMapper(G)
        router = Router(G, mapper)

        return router

    def test_routing_performance(self, setup_router):
        """Test that routing completes in reasonable time."""
        import time

        router = setup_router

        origin = (40.9856, 29.0298)
        dest = (40.9638, 29.0408)

        start = time.time()
        result = router.compute_shortest_path(
            origin[0], origin[1],
            dest[0], dest[1]
        )
        elapsed = time.time() - start

        # Routing should complete in less than 1 second
        assert elapsed < 1.0

        if result['success']:
            # Computation time in result should also be reasonable
            assert result['computation_time'] < 1.0

    def test_batch_coordinate_mapping(self, setup_router):
        """Test batch coordinate mapping performance."""
        import time

        router = setup_router
        mapper = router.node_mapper

        # Create 100 test coordinates around Kadıköy
        coordinates = [
            (40.98 + i*0.001, 29.02 + i*0.001)
            for i in range(100)
        ]

        start = time.time()
        nodes = mapper.batch_find_nearest_nodes(coordinates)
        elapsed = time.time() - start

        # Should complete in less than 1 second
        assert elapsed < 1.0

        # Should find most nodes
        found = len([n for n in nodes if n is not None])
        assert found > 50  # At least half should be found


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_graph_loader_invalid_location(self):
        """Test handling of invalid location."""
        from worldcar.graph_loader import GraphLoader

        loader = GraphLoader("InvalidLocationThatDoesNotExist12345")

        # Should raise an error when trying to download
        with pytest.raises(ValueError):
            loader.download_network()

    def test_empty_graph_router(self):
        """Test that creating router with empty graph raises error."""
        from worldcar.algorithms import Router
        from worldcar.node_mapper import NodeMapper

        G = nx.MultiDiGraph()  # Empty graph

        with pytest.raises(ValueError):
            mapper = NodeMapper(G)

    def test_coordinates_outside_network(self):
        """Test coordinates far from network."""
        from worldcar.graph_loader import GraphLoader
        from worldcar.node_mapper import NodeMapper

        loader = GraphLoader()
        G = loader.get_or_create_graph()
        mapper = NodeMapper(G)

        # Coordinates very far from Kadıköy (e.g., North Pole)
        node = mapper.find_nearest_node(89.0, 0.0)

        # Should not find a node (too far from network)
        assert node is None
