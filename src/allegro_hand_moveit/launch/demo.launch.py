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
