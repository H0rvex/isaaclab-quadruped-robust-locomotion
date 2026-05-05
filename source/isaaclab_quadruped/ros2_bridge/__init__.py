"""Local ROS 2 bridge interface contracts.

The bridge package defines topic names, message-shaped dictionaries, and config
validation for a future ROS 2 integration. It is not a ROS node and does not
require ROS client libraries.
"""

from isaaclab_quadruped.ros2_bridge.bridge_config import BridgeConfig
from isaaclab_quadruped.ros2_bridge.fake_state import FakeStatePublisher
from isaaclab_quadruped.ros2_bridge.topic_contracts import Ros2TopicContracts, TopicContract

__all__ = [
    "BridgeConfig",
    "FakeStatePublisher",
    "Ros2TopicContracts",
    "TopicContract",
]
