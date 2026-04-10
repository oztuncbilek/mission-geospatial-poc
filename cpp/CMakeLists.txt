cmake_minimum_required(VERSION 3.15)
project(mission_query_client CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Mac (Apple Silicon) Homebrew 
include_directories(/opt/homebrew/include)
link_directories(/opt/homebrew/lib)

include_directories(/opt/homebrew/opt/libpq/include)
link_directories(/opt/homebrew/opt/libpq/lib)

add_executable(mission_client main.cpp)

target_link_libraries(mission_client pqxx pq)