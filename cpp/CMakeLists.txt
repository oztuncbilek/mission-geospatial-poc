cmake_minimum_required(VERSION 3.15)
project(mission_query_client CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(libpqxx REQUIRED)

add_executable(mission_client main.cpp)
target_link_libraries(mission_client PRIVATE libpqxx::pqxx)