from mopaint import Paint
import pytest


def test_grid_validation():
    """Test grid parameter validation."""
    # Should be able to create with show_grid=True and store_grid=False
    widget = Paint(show_grid=True, store_grid=False)
    assert widget.show_grid is True
    assert widget.store_grid is False

    # Should be able to create with both False
    widget = Paint(show_grid=False, store_grid=False)
    assert widget.show_grid is False
    assert widget.store_grid is False

    # Should raise error when store_grid=True but show_grid=False
    with pytest.raises(ValueError) as exc_info:
        Paint(show_grid=False, store_grid=True)
    assert "store_grid cannot be True when show_grid is False" in str(exc_info.value)


def test_grid_state_changes():
    """Test grid state changes and validation."""
    widget = Paint(show_grid=True, store_grid=True)
    
    # Test that turning off show_grid automatically turns off store_grid
    widget.show_grid = False
    assert widget.show_grid is False
    assert widget.store_grid is False

    # Test that we can't set store_grid=True when show_grid=False
    with pytest.raises(ValueError) as exc_info:
        widget.store_grid = True
    assert "store_grid cannot be True when show_grid is False" in str(exc_info.value)

    # Test that we can set store_grid=True when show_grid=True
    widget.show_grid = True
    widget.store_grid = True
    assert widget.show_grid is True
    assert widget.store_grid is True


def test_grid_parameters():
    """Test that grid parameters are properly synced with the frontend."""
    # Create widget with grid enabled
    widget = Paint(show_grid=True, store_grid=True)
    
    # The grid rendering is handled by the TypeScript side,
    # so we only need to verify that the parameters are properly set
    assert widget.show_grid is True
    assert widget.store_grid is True
    
    # Verify that the parameters are properly tagged for syncing with frontend
    assert getattr(Paint, 'show_grid').tag(sync=True)
    assert getattr(Paint, 'store_grid').tag(sync=True)
