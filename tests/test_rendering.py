"""Unit tests for rendering module"""
import unittest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from rendering import ensure_output_dir, render_diagram, display_results


class TestRendering(unittest.TestCase):
    """Test cases for the rendering module"""

    def setUp(self):
        """Set up test fixtures"""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_output_dir = os.environ.get('OUTPUT_DIR')

    def tearDown(self):
        """Clean up after tests"""
        # Remove the temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

        # Restore original OUTPUT_DIR if it existed
        if self.original_output_dir:
            os.environ['OUTPUT_DIR'] = self.original_output_dir

    @patch('rendering.OUTPUT_DIR')
    def test_ensure_output_dir_creates_directory(self, mock_output_dir):
        """Test that ensure_output_dir creates the output directory"""
        test_path = Path(self.test_dir) / "test_output"
        mock_output_dir.__str__ = lambda x: str(test_path)
        mock_output_dir.__fspath__ = lambda x: str(test_path)

        # Directory should not exist yet
        self.assertFalse(test_path.exists())

        # Call ensure_output_dir with patched OUTPUT_DIR
        with patch('rendering.Path') as mock_path_class:
            mock_path_instance = MagicMock()
            mock_path_class.return_value = mock_path_instance

            result = ensure_output_dir()

            # Verify mkdir was called with correct parameters
            mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('rendering.subprocess.run')
    @patch('rendering.OUTPUT_DIR')
    def test_render_diagram_success(self, mock_output_dir, mock_subprocess):
        """Test successful diagram rendering"""
        # Set up mocks
        test_output_path = Path(self.test_dir) / "output"
        test_output_path.mkdir(parents=True, exist_ok=True)
        mock_output_dir.__str__ = lambda x: str(test_output_path)

        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        # Test dot code
        test_dot_code = "digraph Test {A -> B;}"

        # Render diagram
        with patch('rendering.ensure_output_dir', return_value=test_output_path):
            output_file, source_file = render_diagram(test_dot_code, "test")

        # Verify subprocess was called correctly
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args

        # Check that dot command was called
        self.assertEqual(call_args[0][0][0], 'dot')

        # Verify source file was created
        self.assertTrue(os.path.exists(source_file))
        with open(source_file, 'r') as f:
            self.assertEqual(f.read(), test_dot_code)

    @patch('rendering.subprocess.run')
    @patch('rendering.OUTPUT_DIR')
    def test_render_diagram_failure(self, mock_output_dir, mock_subprocess):
        """Test diagram rendering failure"""
        # Set up mocks
        test_output_path = Path(self.test_dir) / "output"
        test_output_path.mkdir(parents=True, exist_ok=True)

        # Mock failed subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Syntax error in dot code"
        mock_subprocess.return_value = mock_result

        test_dot_code = "invalid dot code"

        # Should raise RuntimeError
        with patch('rendering.ensure_output_dir', return_value=test_output_path):
            with self.assertRaises(RuntimeError) as context:
                render_diagram(test_dot_code, "test")

            self.assertIn("Rendering failed", str(context.exception))

    @patch('rendering.subprocess.run')
    @patch('rendering.OUTPUT_DIR')
    def test_render_diagram_graphviz_not_found(self, mock_output_dir, mock_subprocess):
        """Test handling when graphviz is not installed"""
        test_output_path = Path(self.test_dir) / "output"
        test_output_path.mkdir(parents=True, exist_ok=True)

        # Mock FileNotFoundError
        mock_subprocess.side_effect = FileNotFoundError()

        test_dot_code = "digraph { A -> B; }"

        with patch('rendering.ensure_output_dir', return_value=test_output_path):
            with self.assertRaises(RuntimeError) as context:
                render_diagram(test_dot_code, "test")

            self.assertIn("Graphviz 'dot' command not found", str(context.exception))

    @patch('rendering.subprocess.run')
    @patch('rendering.OUTPUT_DIR')
    def test_render_diagram_timeout(self, mock_output_dir, mock_subprocess):
        """Test handling of rendering timeout"""
        test_output_path = Path(self.test_dir) / "output"
        test_output_path.mkdir(parents=True, exist_ok=True)

        # Mock timeout
        import subprocess
        mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd='dot', timeout=30)

        test_dot_code = "digraph { A -> B; }"

        with patch('rendering.ensure_output_dir', return_value=test_output_path):
            with self.assertRaises(RuntimeError) as context:
                render_diagram(test_dot_code, "test")

            self.assertIn("Rendering timed out", str(context.exception))

    @patch('builtins.print')
    def test_display_results(self, mock_print):
        """Test display_results function"""
        output_file = "/path/to/diagram.svg"
        source_file = "/path/to/diagram.dot"

        display_results(output_file, source_file)

        # Verify print was called
        self.assertTrue(mock_print.called)

        # Check that output contains expected information
        printed_output = ' '.join([str(call[0][0]) for call in mock_print.call_args_list])
        self.assertIn("DIAGRAM GENERATION COMPLETE", printed_output)
        self.assertIn(output_file, printed_output)
        self.assertIn(source_file, printed_output)


if __name__ == '__main__':
    unittest.main()
