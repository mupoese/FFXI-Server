/*
===========================================================================

  Copyright (c) 2025 LandSandBoat Dev Teams

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see http://www.gnu.org/licenses/

===========================================================================
*/

#pragma once

#include "common/cbasetypes.h"
#include "common/tracy.h"
#include <memory>
#include <vector>
#include <unordered_map>
#include <functional>

class CBaseEntity;

namespace spatial
{
    // 3D position structure for spatial calculations
    struct Position3D
    {
        float x, y, z;
        
        Position3D() : x(0.0f), y(0.0f), z(0.0f) {}
        Position3D(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}
        
        auto distanceSquared(const Position3D& other) const -> float
        {
            const float dx = x - other.x;
            const float dy = y - other.y;
            const float dz = z - other.z;
            return dx * dx + dy * dy + dz * dz;
        }
        
        auto distance(const Position3D& other) const -> float
        {
            return std::sqrt(distanceSquared(other));
        }
    };

    // Axis-aligned bounding box for spatial queries
    struct AABB
    {
        Position3D min, max;
        
        AABB() = default;
        AABB(const Position3D& min_, const Position3D& max_) : min(min_), max(max_) {}
        
        auto contains(const Position3D& point) const -> bool
        {
            return point.x >= min.x && point.x <= max.x &&
                   point.y >= min.y && point.y <= max.y &&
                   point.z >= min.z && point.z <= max.z;
        }
        
        auto intersects(const AABB& other) const -> bool
        {
            return !(max.x < other.min.x || min.x > other.max.x ||
                     max.y < other.min.y || min.y > other.max.y ||
                     max.z < other.min.z || min.z > other.max.z);
        }
    };

    // Forward declarations
    class SpatialNode;
    class SpatialGrid;

    // Entity wrapper for spatial partitioning
    struct SpatialEntity
    {
        CBaseEntity* entity;
        Position3D   position;
        uint32       lastUpdateTime;
        
        SpatialEntity(CBaseEntity* ent, const Position3D& pos) 
            : entity(ent), position(pos), lastUpdateTime(0) {}
    };

    // Octree node for hierarchical spatial partitioning
    class SpatialNode
    {
    public:
        static constexpr size_t MAX_ENTITIES_PER_NODE = 8;
        static constexpr size_t MAX_DEPTH = 6;

        SpatialNode(const AABB& bounds, size_t depth = 0);
        ~SpatialNode();

        // Entity management
        void insertEntity(std::unique_ptr<SpatialEntity> entity);
        void removeEntity(CBaseEntity* entity);
        void updateEntity(CBaseEntity* entity, const Position3D& newPos);

        // Spatial queries
        auto queryRange(const AABB& queryBounds, std::vector<CBaseEntity*>& results) const -> void;
        auto queryRadius(const Position3D& center, float radius, std::vector<CBaseEntity*>& results) const -> void;
        auto findNearestEntity(const Position3D& position, CBaseEntity* exclude = nullptr) const -> CBaseEntity*;

        // Node maintenance
        void subdivide();
        void clear();
        auto getEntityCount() const -> size_t;

    private:
        AABB                                        bounds_;
        size_t                                      depth_;
        std::vector<std::unique_ptr<SpatialEntity>> entities_;
        std::unique_ptr<SpatialNode>                children_[8];
        bool                                        isLeaf_;

        auto getChildIndex(const Position3D& position) const -> size_t;
        void insertIntoChild(std::unique_ptr<SpatialEntity> entity);
    };

    // High-level spatial partitioning manager
    class SpatialPartitioningSystem
    {
    public:
        SpatialPartitioningSystem();
        ~SpatialPartitioningSystem();

        // System initialization
        void initialize(const AABB& worldBounds);
        void shutdown();

        // Entity management
        void addEntity(CBaseEntity* entity);
        void removeEntity(CBaseEntity* entity);
        void updateEntityPosition(CBaseEntity* entity);

        // Spatial queries with performance optimization
        auto getEntitiesInRange(const Position3D& center, float range) -> std::vector<CBaseEntity*>;
        auto getEntitiesInArea(const AABB& area) -> std::vector<CBaseEntity*>;
        auto findNearestEntity(const Position3D& position, CBaseEntity* exclude = nullptr) -> CBaseEntity*;
        auto getEntitiesOfType(const Position3D& center, float range, uint8 entityType) -> std::vector<CBaseEntity*>;

        // Performance monitoring
        auto getQueryCount() const -> uint32 { return queryCount_; }
        auto getUpdateCount() const -> uint32 { return updateCount_; }
        auto getAverageQueryTime() const -> double { return averageQueryTime_; }
        void resetStatistics();

        // Grid-based optimization for dense areas
        void enableGridOptimization(bool enable) { useGridOptimization_ = enable; }
        void setGridCellSize(float cellSize) { gridCellSize_ = cellSize; }

    private:
        std::unique_ptr<SpatialNode>                           rootNode_;
        std::unique_ptr<SpatialGrid>                          grid_;
        std::unordered_map<CBaseEntity*, Position3D>          entityPositions_;
        
        // Performance tracking
        mutable uint32 queryCount_;
        mutable uint32 updateCount_;
        mutable double totalQueryTime_;
        mutable double averageQueryTime_;
        
        // Configuration
        bool  useGridOptimization_;
        float gridCellSize_;
        AABB  worldBounds_;
        bool  initialized_;

        // Helper methods
        auto getEntityPosition(CBaseEntity* entity) const -> Position3D;
        void updatePerformanceStats(double queryTime) const;
    };

    // Grid-based spatial partitioning for dense areas
    class SpatialGrid
    {
    public:
        SpatialGrid(const AABB& bounds, float cellSize);
        ~SpatialGrid();

        void addEntity(CBaseEntity* entity, const Position3D& position);
        void removeEntity(CBaseEntity* entity, const Position3D& position);
        void updateEntity(CBaseEntity* entity, const Position3D& oldPos, const Position3D& newPos);

        auto queryRange(const AABB& queryBounds) const -> std::vector<CBaseEntity*>;
        auto queryRadius(const Position3D& center, float radius) const -> std::vector<CBaseEntity*>;

    private:
        struct GridCell
        {
            std::vector<CBaseEntity*> entities;
        };

        AABB   bounds_;
        float  cellSize_;
        size_t gridWidth_;
        size_t gridHeight_;
        size_t gridDepth_;
        std::vector<GridCell> cells_;

        auto getCellIndex(const Position3D& position) const -> size_t;
        auto isValidCell(size_t x, size_t y, size_t z) const -> bool;
    };

    // Global spatial partitioning system access
    auto getSpatialSystem() -> SpatialPartitioningSystem&;
    void initializeSpatialSystem(const AABB& worldBounds);
    void shutdownSpatialSystem();

} // namespace spatial