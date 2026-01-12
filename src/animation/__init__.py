"""
Animation module for smooth car movement along computed paths.

Provides smooth interpolation, camera follow, and game-like visualization
for pathfinding results on real-world road networks.
"""

from .path_interpolator import PathInterpolator, InterpolationMethod
from .car_animator import CarAnimator
from .camera_controller import CameraController
from .animation_controller import AnimationController

__all__ = [
    "PathInterpolator",
    "InterpolationMethod",
    "CarAnimator",
    "CameraController",
    "AnimationController"
]
