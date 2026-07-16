cmake_minimum_required(VERSION 3.8)
project(sprint_sbr)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)

find_package(rosidl_default_generators REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Object.msg"
  "msg/ObjectArray.msg"
)

install(DIRECTORY
  launch
  world
  models
  config
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/twist2thrust.py
  scripts/perception_node.py
  scripts/sensor_hub.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
