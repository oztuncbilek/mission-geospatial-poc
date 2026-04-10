#include <iomanip>
#include <iostream>
#include <string>
#include <pqxx/pqxx>

const std::string CONN_STR =
    "host=localhost port=5432 dbname=mission_geo "
    "user=mission_user password=mission_pass";

void separator(const std::string& title) {
    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  " << title << "\n";
    std::cout << std::string(60, '-') << "\n";
}

void summary(pqxx::work& txn) {
    separator("Mission Database Summary");
    const std::vector<std::pair<std::string, std::string>> tables = {
        {"mission.mission_areas", "Mission Areas"},
        {"mission.flight_paths",  "Flight Paths"},
        {"mission.observations",  "Observations"},
        {"mission.no_fly_zones",  "No-Fly Zones"},
        {"mission.targets",       "Targets"},
    };
    for (const auto& [tbl, label] : tables) {
        auto row = txn.exec1("SELECT COUNT(*) FROM " + tbl);
        std::cout << "  " << std::left << std::setw(22) << label
                  << ": " << row[0].as<int>() << " features\n";
    }
}

void targets_in_area(pqxx::work& txn) {
    separator("Targets Inside Mission Area #1  [ST_Contains]");
    auto r = txn.exec(R"(
        SELECT t.id, t.name, t.priority, t.status,
               ST_AsText(t.geom) AS location
        FROM   mission.targets t
        JOIN   mission.mission_areas a ON ST_Contains(a.geom, t.geom)
        WHERE  a.id = 1
        ORDER  BY t.priority
    )");
    if (r.empty()) { std::cout << "  No targets inside mission area.\n"; return; }
    std::cout << "  " << std::left
              << std::setw(6) << "ID"
              << std::setw(14) << "Name"
              << std::setw(10) << "Priority"
              << std::setw(14) << "Status"
              << "Location\n";
    std::cout << "  " << std::string(56, '-') << "\n";
    for (const auto& row : r) {
        std::cout << "  "
                  << std::setw(6)  << row["id"].as<int>()
                  << std::setw(14) << row["name"].c_str()
                  << std::setw(10) << row["priority"].as<int>()
                  << std::setw(14) << row["status"].c_str()
                  << row["location"].c_str() << "\n";
    }
}

void nearest_target(pqxx::work& txn) {
    separator("Nearest Target per Observation  [KNN <->]");
    auto r = txn.exec(R"(
        SELECT o.id        AS obs_id,
               o.observation_type,
               t.id        AS target_id,
               t.name      AS target_name,
               ROUND(ST_Distance(
                   ST_Transform(o.geom, 32632),
                   ST_Transform(t.geom, 32632)
               )::numeric, 2) AS dist_m
        FROM mission.observations o
        CROSS JOIN LATERAL (
            SELECT t2.*
            FROM   mission.targets t2
            ORDER  BY o.geom <-> t2.geom
            LIMIT  1
        ) t
        ORDER BY o.id
        LIMIT 10
    )");
    if (r.empty()) { std::cout << "  No observations found.\n"; return; }
    std::cout << "  " << std::left
              << std::setw(8)  << "Obs ID"
              << std::setw(22) << "Type"
              << std::setw(10) << "Target"
              << std::setw(16) << "Target Name"
              << "Distance (m)\n";
    std::cout << "  " << std::string(56, '-') << "\n";
    for (const auto& row : r) {
        std::cout << "  "
                  << std::setw(8)  << row["obs_id"].as<int>()
                  << std::setw(22) << row["observation_type"].c_str()
                  << std::setw(10) << row["target_id"].as<int>()
                  << std::setw(16) << row["target_name"].c_str()
                  << row["dist_m"].c_str() << " m\n";
    }
}

void no_fly_intersections(pqxx::work& txn) {
    separator("Flight Paths Intersecting No-Fly Zones  [ST_Intersects]");
    auto r = txn.exec(R"(
        SELECT f.id AS path_id, f.platform_name,
               z.name AS zone_name, z.restriction_type
        FROM   mission.flight_paths f
        JOIN   mission.no_fly_zones z ON ST_Intersects(f.geom, z.geom)
        ORDER  BY f.id
    )");
    if (r.empty()) {
        std::cout << "  [CLEAR] No flight path intersects a no-fly zone.\n";
        return;
    }
    std::cout << "  [WARNING] " << r.size() << " conflict(s) detected!\n\n";
    for (const auto& row : r) {
        std::cout << "  Path " << row["path_id"].as<int>()
                  << " (" << row["platform_name"].c_str() << ")"
                  << "  →  zone: " << row["zone_name"].c_str()
                  << "  [" << row["restriction_type"].c_str() << "]\n";
    }
}

void bbox_observations(pqxx::work& txn) {
    separator("Observations in BBox  [&& ST_MakeEnvelope]");
    auto r = txn.exec(R"(
        SELECT id, observation_type, confidence, source_name,
               ST_AsText(geom) AS location
        FROM   mission.observations
        WHERE  geom && ST_MakeEnvelope(11.530, 11.575, 48.130, 48.165, 4326)
        ORDER  BY confidence DESC
        LIMIT  15
    )");
    std::cout << "  BBox: [11.530, 48.130] → [11.575, 48.165]\n";
    std::cout << "  Found: " << r.size() << " observation(s)\n\n";
    for (const auto& row : r) {
        std::cout << "  ID " << std::setw(4) << row["id"].as<int>()
                  << "  | " << std::setw(20) << row["observation_type"].c_str()
                  << "  | conf: " << row["confidence"].c_str()
                  << "\n    " << row["location"].c_str() << "\n";
    }
}

int main() {
    std::cout << "\n";
    std::cout << "  ╔══════════════════════════════════════════════════╗\n";
    std::cout << "  ║   MISSION GEOSPATIAL POC — C++ Query Client      ║\n";
    std::cout << "  ║   PostGIS Spatial Queries via libpqxx             ║\n";
    std::cout << "  ╚══════════════════════════════════════════════════╝\n";

    try {
        pqxx::connection conn(CONN_STR);
        if (!conn.is_open()) {
            std::cerr << "[ERROR] DB bağlantısı kurulamadı.\n";
            return 1;
        }
        std::cout << "\n  [OK] Bağlandı: " << conn.dbname()
                  << " @ " << conn.hostname() << "\n";

        pqxx::work txn(conn);
        txn.exec("SET search_path TO mission, public;");

        summary(txn);
        targets_in_area(txn);
        nearest_target(txn);
        no_fly_intersections(txn);
        bbox_observations(txn);

        txn.commit();

    } catch (const pqxx::sql_error& e) {
        std::cerr << "[SQL ERROR] " << e.what() << "\n"
                  << "  Query: "    << e.query() << "\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "[ERROR] " << e.what() << "\n";
        return 1;
    }

    std::cout << "\n" << std::string(60, '=') << "\n";
    std::cout << "  Tüm sorgular başarıyla tamamlandı.\n\n";
    return 0;
}