#!/usr/bin/env python3
"""A stand-in for allegro_node_grasp that needs no CAN bus.

Speaks exactly the two topics the real driver speaks, so a bringup can swap between
mock and hardware without anything downstream changing:

    subscribes  allegroHand/joint_cmd     sensor_msgs/JointState
    publishes   allegroHand/joint_states  sensor_msgs/JointState

Commands are read POSITIONALLY out of msg.position, matching
AllegroNodeGrasp::setJointCallback, which does `desired_position[i] = msg->position[i]`
and ignores msg.name entirely. A command with fewer than 16 entries is rejected rather
than half-applied, which is friendlier than the driver but keeps the same contract for
well-formed messages.

The reported position chases the command through a first-order lag so RViz shows motion
with a plausible shape instead of teleporting. This is a visualisation aid, not a model
of the hand: there is no torque, no BHand grasp library, and no joint limit enforcement
beyond what the URDF declares.
"""

import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

# Driver index order. Must stay identical to jointNames[] in
# allegro_hand_controllers/src/allegro_node.cpp -- the command topic is positional, so a
# reordering here would silently drive the wrong joints.
JOINT_NAMES = [
    "joint_0_0", "joint_1_0", "joint_2_0", "joint_3_0",
    "joint_4_0", "joint_5_0", "joint_6_0", "joint_7_0",
    "joint_8_0", "joint_9_0", "joint_10_0", "joint_11_0",
    "joint_12_0", "joint_13_0", "joint_14_0", "joint_15_0",
]
DOF_JOINTS = len(JOINT_NAMES)


class AllegroMockNode(Node):
    def __init__(self) -> None:
        super().__init__("allegro_mock_node")

        self.declare_parameter("publish_rate", 100.0)
        self.declare_parameter("tau", 0.1)

        publish_rate = self.get_parameter("publish_rate").value
        self._tau = self.get_parameter("tau").value
        self._dt = 1.0 / publish_rate

        self._desired = [0.0] * DOF_JOINTS
        self._current = [0.0] * DOF_JOINTS
        self._velocity = [0.0] * DOF_JOINTS

        self._joint_state_pub = self.create_publisher(
            JointState, "allegroHand/joint_states", 3
        )
        self._joint_cmd_sub = self.create_subscription(
            JointState, "allegroHand/joint_cmd", self._joint_cmd_cb, 1
        )
        self._timer = self.create_timer(self._dt, self._update)

        self.get_logger().info(
            f"Mock Allegro hand up: {DOF_JOINTS} joints at {publish_rate:g} Hz, "
            f"tau={self._tau:g}s. No CAN bus is being touched."
        )

    def _joint_cmd_cb(self, msg: JointState) -> None:
        if len(msg.position) < DOF_JOINTS:
            self.get_logger().warn(
                f"Ignoring joint_cmd with {len(msg.position)} positions; "
                f"the driver reads {DOF_JOINTS} positionally.",
                throttle_duration_sec=5.0,
            )
            return
        self._desired = [float(p) for p in msg.position[:DOF_JOINTS]]

    def _update(self) -> None:
        # First-order lag: alpha is the fraction of the remaining error closed each tick.
        alpha = 1.0 if self._tau <= 0.0 else 1.0 - math.exp(-self._dt / self._tau)
        for i in range(DOF_JOINTS):
            step = alpha * (self._desired[i] - self._current[i])
            self._current[i] += step
            self._velocity[i] = step / self._dt

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = self._current
        msg.velocity = self._velocity
        msg.effort = [0.0] * DOF_JOINTS
        self._joint_state_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = AllegroMockNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
