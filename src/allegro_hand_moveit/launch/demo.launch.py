
###change2###

from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    moveit_config = MoveItConfigsBuilder("allegro_hand_right", package_name="allegro_hand_moveit").to_moveit_configs()

    demo_launch = generate_demo_launch(moveit_config)
    
    save_joint_angles_node = Node(
        package='allegro_hand_moveit',
        executable='save_joint_angles',
        name='save_joint_angles',
        output='screen'
    )
    
    ld = LaunchDescription()
    

    for action in demo_launch.entities: 
        ld.add_action(action)
    
    ld.add_action(save_joint_angles_node)
    
    return ld


###change3###

# from moveit_configs_utils import MoveItConfigsBuilder
# from moveit_configs_utils.launches import generate_demo_launch

# from launch import LaunchDescription
# from launch.actions import (
#     DeclareLaunchArgument,
#     IncludeLaunchDescription,
# )
# from launch.conditions import IfCondition
# from launch.launch_description_sources import PythonLaunchDescriptionSource
# from launch.substitutions import LaunchConfiguration

# from launch_ros.actions import Node
# from launch_ros.parameter_descriptions import ParameterValue

# from srdfdom.srdf import SRDF


# def launch_setup(moveit_config):
#     """
#     Launches a self contained demo

#     Includes
#      * static_virtual_joint_tfs
#      * robot_state_publisher
#      * move_group
#      * moveit_rviz
#      * warehouse_db (optional)
#      * ros2_control_node + controller spawners
#     """
#     ld = LaunchDescription()

#     # If there are virtual joints, broadcast static tf by including virtual_joints launch
#     # virtual_joints_launch = (
#     #     moveit_config.package_path / "launch/static_virtual_joint_tfs.launch.py"
#     # )
#     # if virtual_joints_launch.exists():
#     #     ld.add_action(
#     #         IncludeLaunchDescription(
#     #             PythonLaunchDescriptionSource(str(virtual_joints_launch)),
#     #         )
#     #     )

#     # Given the published joint states, publish tf for the robot links
#     #delto_3f_driver 
    
#     ld.add_action(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 str(moveit_config.package_path / "launch/rsp.launch.py")
#             ),
#         )
#     )

#     ld.add_action(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 str(moveit_config.package_path / "launch/move_group.launch.py")
#             ),
#         )
#     )

#     # Run Rviz and load the default config to see the state of the move_group node
#     ld.add_action(
#         IncludeLaunchDescription(
#             PythonLaunchDescriptionSource(
#                 str(moveit_config.package_path / "launch/moveit_rviz.launch.py")
#             )
#         )
#     )

#     # Fake joint driver
#     ld.add_action(
#         Node(
#             package="controller_manager",
#             executable="ros2_control_node",
#             parameters=[
#                 moveit_config.robot_description,
#                 str(moveit_config.package_path / "config/ros2_controllers.yaml"),
#             ],
#         )
#     )

#     return ld


# def generate_launch_description():
#     moveit_config = (MoveItConfigsBuilder("allegro_hand_right", package_name="allegro_hand_moveit")
#                      .robot_description(file_path = "config/allegro_hand_right_A.urdf.xacro")
#                      .to_moveit_configs()
#                      )
#     return launch_setup(moveit_config)
