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

#include "spatial_partitioning.h"

#include "common/logging.h"
#include "common/timer.h"
#include "common/tracy.h"

#include "entities/baseentity.h"

#include <algorithm>
#include <cmath>
#include <chrono>

namespace spatial
{
    namespace
    {
        std::unique_ptr<SpatialPartitioningSystem> g_spatialSystem;
    }

    // SpatialNode implementation
    SpatialNode::SpatialNode(const AABB& bounds, size_t depth)
    : bounds_(bounds)
    , depth_(depth)
    , isLeaf_(true)
    {
        TracyZoneScoped;
        entities_.reserve(MAX_ENTITIES_PER_NODE);
        
        // Initialize children to nullptr
        for (auto& child : children_)
        {
            child = nullptr;
        }
    }

    SpatialNode::~SpatialNode()
    {
        TracyZoneScoped;
        clear();
    }

    void SpatialNode::insertEntity(std::unique_ptr<SpatialEntity> entity)
    {
        TracyZoneScoped;
        
        if (!entity || !entity->entity)
        {
            return;
        }

        // If this is not a leaf, insert into appropriate child
        if (!isLeaf_)
        {
            insertIntoChild(std::move(entity));
            return;
        }

        // Add to this node
        entities_.push_back(std::move(entity));

        // Check if we need to subdivide
        if (entities_.size() > MAX_ENTITIES_PER_NODE && depth_ < MAX_DEPTH)
        {
            subdivide();
        }
    }

    void SpatialNode::removeEntity(CBaseEntity* entity)
    {
        TracyZoneScoped;
        
        if (!entity)
        {
            return;
        }

        if (isLeaf_)
        {
            // Remove from this node
            entities_.erase(
                std::remove_if(entities_.begin(), entities_.end(),
                    [entity](const std::unique_ptr<SpatialEntity>& spatialEnt) {
                        return spatialEnt->entity == entity;
                    }),
                entities_.end());
        }
        else
        {
            // Remove from children
            for (auto& child : children_)
            {
                if (child)
                {
                    child->removeEntity(entity);
                }
            }
        }
    }

    void SpatialNode::updateEntity(CBaseEntity* entity, const Position3D& newPos)
    {
        TracyZoneScoped;
        
        // For now, we do a simple remove and re-insert
        // In a more optimized version, we could check if the entity
        // stays within the same node bounds
        removeEntity(entity);
        
        if (bounds_.contains(newPos))
        {
            auto spatialEntity = std::make_unique<SpatialEntity>(entity, newPos);
            spatialEntity->lastUpdateTime = server_clock::now().time_since_epoch().count();
            insertEntity(std::move(spatialEntity));
        }
    }

    auto SpatialNode::queryRange(const AABB& queryBounds, std::vector<CBaseEntity*>& results) const -> void
    {
        TracyZoneScoped;
        
        // Check if query bounds intersect with this node
        if (!bounds_.intersects(queryBounds))
        {
            return;
        }

        if (isLeaf_)
        {
            // Check entities in this node
            for (const auto& entity : entities_)
            {
                if (entity && entity->entity && queryBounds.contains(entity->position))
                {
                    results.push_back(entity->entity);
                }
            }
        }
        else
        {
            // Query children
            for (const auto& child : children_)
            {
                if (child)
                {
                    child->queryRange(queryBounds, results);
                }
            }
        }
    }

    auto SpatialNode::queryRadius(const Position3D& center, float radius, std::vector<CBaseEntity*>& results) const -> void
    {
        TracyZoneScoped;
        
        // Create AABB for radius query
        const float r = radius;
        AABB radiusBounds(
            Position3D(center.x - r, center.y - r, center.z - r),
            Position3D(center.x + r, center.y + r, center.z + r)
        );

        // First check if this node intersects with the radius bounds
        if (!bounds_.intersects(radiusBounds))
        {
            return;
        }

        const float radiusSquared = radius * radius;

        if (isLeaf_)
        {
            // Check entities in this node
            for (const auto& entity : entities_)
            {
                if (entity && entity->entity)
                {
                    if (entity->position.distanceSquared(center) <= radiusSquared)
                    {
                        results.push_back(entity->entity);
                    }
                }
            }
        }
        else
        {
            // Query children
            for (const auto& child : children_)
            {
                if (child)
                {
                    child->queryRadius(center, radius, results);
                }
            }
        }
    }

    auto SpatialNode::findNearestEntity(const Position3D& position, CBaseEntity* exclude) const -> CBaseEntity*
    {
        TracyZoneScoped;
        
        CBaseEntity* nearest = nullptr;
        float nearestDistanceSquared = std::numeric_limits<float>::max();

        if (isLeaf_)
        {
            for (const auto& entity : entities_)
            {
                if (entity && entity->entity && entity->entity != exclude)
                {
                    const float distSquared = entity->position.distanceSquared(position);
                    if (distSquared < nearestDistanceSquared)
                    {
                        nearest = entity->entity;
                        nearestDistanceSquared = distSquared;
                    }
                }
            }
        }
        else
        {
            for (const auto& child : children_)
            {
                if (child)
                {
                    auto candidate = child->findNearestEntity(position, exclude);
                    if (candidate)
                    {
                        // We would need to get the position of the candidate to compare distances
                        // For simplicity, return the first found candidate
                        if (!nearest)
                        {
                            nearest = candidate;
                        }
                    }
                }
            }
        }

        return nearest;
    }

    void SpatialNode::subdivide()
    {
        TracyZoneScoped;
        
        if (!isLeaf_ || depth_ >= MAX_DEPTH)
        {
            return;
        }

        // Calculate child bounds
        const Position3D center(
            (bounds_.min.x + bounds_.max.x) * 0.5f,
            (bounds_.min.y + bounds_.max.y) * 0.5f,
            (bounds_.min.z + bounds_.max.z) * 0.5f
        );

        // Create 8 children (octree)
        const Position3D childSize(
            (bounds_.max.x - bounds_.min.x) * 0.5f,
            (bounds_.max.y - bounds_.min.y) * 0.5f,
            (bounds_.max.z - bounds_.min.z) * 0.5f
        );

        // Define child bounds for octree subdivision
        const AABB childBounds[8] = {
            // Bottom 4 children (lower Y)
            AABB(bounds_.min, center),
            AABB(Position3D(center.x, bounds_.min.y, bounds_.min.z), Position3D(bounds_.max.x, center.y, center.z)),
            AABB(Position3D(bounds_.min.x, bounds_.min.y, center.z), Position3D(center.x, center.y, bounds_.max.z)),
            AABB(Position3D(center.x, bounds_.min.y, center.z), Position3D(bounds_.max.x, center.y, bounds_.max.z)),
            // Top 4 children (upper Y)
            AABB(Position3D(bounds_.min.x, center.y, bounds_.min.z), Position3D(center.x, bounds_.max.y, center.z)),
            AABB(Position3D(center.x, center.y, bounds_.min.z), Position3D(bounds_.max.x, bounds_.max.y, center.z)),
            AABB(Position3D(bounds_.min.x, center.y, center.z), Position3D(center.x, bounds_.max.y, bounds_.max.z)),
            AABB(center, bounds_.max)
        };

        // Create child nodes
        for (size_t i = 0; i < 8; ++i)
        {
            children_[i] = std::make_unique<SpatialNode>(childBounds[i], depth_ + 1);
        }

        // Redistribute entities to children
        auto tempEntities = std::move(entities_);
        entities_.clear();
        
        for (auto& entity : tempEntities)
        {
            insertIntoChild(std::move(entity));
        }

        isLeaf_ = false;
    }

    void SpatialNode::clear()
    {
        TracyZoneScoped;
        
        entities_.clear();
        
        for (auto& child : children_)
        {
            child.reset();
        }
        
        isLeaf_ = true;
    }

    auto SpatialNode::getEntityCount() const -> size_t
    {
        if (isLeaf_)
        {
            return entities_.size();
        }
        
        size_t count = 0;
        for (const auto& child : children_)
        {
            if (child)
            {
                count += child->getEntityCount();
            }
        }
        return count;
    }

    auto SpatialNode::getChildIndex(const Position3D& position) const -> size_t
    {
        const Position3D center(
            (bounds_.min.x + bounds_.max.x) * 0.5f,
            (bounds_.min.y + bounds_.max.y) * 0.5f,
            (bounds_.min.z + bounds_.max.z) * 0.5f
        );

        size_t index = 0;
        if (position.x >= center.x) index |= 1;
        if (position.y >= center.y) index |= 4;
        if (position.z >= center.z) index |= 2;
        
        return index;
    }

    void SpatialNode::insertIntoChild(std::unique_ptr<SpatialEntity> entity)
    {
        TracyZoneScoped;
        
        const size_t childIndex = getChildIndex(entity->position);
        if (children_[childIndex])
        {
            children_[childIndex]->insertEntity(std::move(entity));
        }
    }

    // SpatialPartitioningSystem implementation
    SpatialPartitioningSystem::SpatialPartitioningSystem()
    : queryCount_(0)
    , updateCount_(0)
    , totalQueryTime_(0.0)
    , averageQueryTime_(0.0)
    , useGridOptimization_(false)
    , gridCellSize_(50.0f)
    , initialized_(false)
    {
        TracyZoneScoped;
    }

    SpatialPartitioningSystem::~SpatialPartitioningSystem()
    {
        TracyZoneScoped;
        shutdown();
    }

    void SpatialPartitioningSystem::initialize(const AABB& worldBounds)
    {
        TracyZoneScoped;
        
        if (initialized_)
        {
            shutdown();
        }

        worldBounds_ = worldBounds;
        rootNode_ = std::make_unique<SpatialNode>(worldBounds);
        
        if (useGridOptimization_)
        {
            grid_ = std::make_unique<SpatialGrid>(worldBounds, gridCellSize_);
        }

        initialized_ = true;
        ShowInfo("SpatialPartitioningSystem: Initialized with bounds (%.1f,%.1f,%.1f) to (%.1f,%.1f,%.1f)",
                 worldBounds.min.x, worldBounds.min.y, worldBounds.min.z,
                 worldBounds.max.x, worldBounds.max.y, worldBounds.max.z);
    }

    void SpatialPartitioningSystem::shutdown()
    {
        TracyZoneScoped;
        
        if (!initialized_)
        {
            return;
        }

        rootNode_.reset();
        grid_.reset();
        entityPositions_.clear();
        
        initialized_ = false;
        ShowInfo("SpatialPartitioningSystem: Shutdown completed");
    }

    void SpatialPartitioningSystem::addEntity(CBaseEntity* entity)
    {
        TracyZoneScoped;
        
        if (!initialized_ || !entity)
        {
            return;
        }

        const auto position = getEntityPosition(entity);
        entityPositions_[entity] = position;

        if (useGridOptimization_ && grid_)
        {
            grid_->addEntity(entity, position);
        }
        else if (rootNode_)
        {
            auto spatialEntity = std::make_unique<SpatialEntity>(entity, position);
            spatialEntity->lastUpdateTime = server_clock::now().time_since_epoch().count();
            rootNode_->insertEntity(std::move(spatialEntity));
        }

        ++updateCount_;
    }

    void SpatialPartitioningSystem::removeEntity(CBaseEntity* entity)
    {
        TracyZoneScoped;
        
        if (!initialized_ || !entity)
        {
            return;
        }

        auto it = entityPositions_.find(entity);
        if (it != entityPositions_.end())
        {
            if (useGridOptimization_ && grid_)
            {
                grid_->removeEntity(entity, it->second);
            }
            else if (rootNode_)
            {
                rootNode_->removeEntity(entity);
            }
            
            entityPositions_.erase(it);
        }

        ++updateCount_;
    }

    void SpatialPartitioningSystem::updateEntityPosition(CBaseEntity* entity)
    {
        TracyZoneScoped;
        
        if (!initialized_ || !entity)
        {
            return;
        }

        const auto newPosition = getEntityPosition(entity);
        auto it = entityPositions_.find(entity);
        
        if (it != entityPositions_.end())
        {
            const auto oldPosition = it->second;
            
            if (useGridOptimization_ && grid_)
            {
                grid_->updateEntity(entity, oldPosition, newPosition);
            }
            else if (rootNode_)
            {
                rootNode_->updateEntity(entity, newPosition);
            }
            
            it->second = newPosition;
        }
        else
        {
            // Entity not tracked yet, add it
            addEntity(entity);
        }

        ++updateCount_;
    }

    auto SpatialPartitioningSystem::getEntitiesInRange(const Position3D& center, float range) -> std::vector<CBaseEntity*>
    {
        TracyZoneScoped;
        
        if (!initialized_)
        {
            return {};
        }

        const auto startTime = std::chrono::high_resolution_clock::now();
        std::vector<CBaseEntity*> results;

        if (useGridOptimization_ && grid_)
        {
            results = grid_->queryRadius(center, range);
        }
        else if (rootNode_)
        {
            rootNode_->queryRadius(center, range, results);
        }

        const auto endTime = std::chrono::high_resolution_clock::now();
        const auto queryTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
        updatePerformanceStats(queryTime);

        ++queryCount_;
        return results;
    }

    auto SpatialPartitioningSystem::getEntitiesInArea(const AABB& area) -> std::vector<CBaseEntity*>
    {
        TracyZoneScoped;
        
        if (!initialized_)
        {
            return {};
        }

        const auto startTime = std::chrono::high_resolution_clock::now();
        std::vector<CBaseEntity*> results;

        if (useGridOptimization_ && grid_)
        {
            results = grid_->queryRange(area);
        }
        else if (rootNode_)
        {
            rootNode_->queryRange(area, results);
        }

        const auto endTime = std::chrono::high_resolution_clock::now();
        const auto queryTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
        updatePerformanceStats(queryTime);

        ++queryCount_;
        return results;
    }

    auto SpatialPartitioningSystem::findNearestEntity(const Position3D& position, CBaseEntity* exclude) -> CBaseEntity*
    {
        TracyZoneScoped;
        
        if (!initialized_ || !rootNode_)
        {
            return nullptr;
        }

        const auto startTime = std::chrono::high_resolution_clock::now();
        auto result = rootNode_->findNearestEntity(position, exclude);
        
        const auto endTime = std::chrono::high_resolution_clock::now();
        const auto queryTime = std::chrono::duration<double, std::milli>(endTime - startTime).count();
        updatePerformanceStats(queryTime);

        ++queryCount_;
        return result;
    }

    auto SpatialPartitioningSystem::getEntitiesOfType(const Position3D& center, float range, uint8 entityType) -> std::vector<CBaseEntity*>
    {
        TracyZoneScoped;
        
        auto entities = getEntitiesInRange(center, range);
        
        // Filter by entity type
        entities.erase(
            std::remove_if(entities.begin(), entities.end(),
                [entityType](CBaseEntity* entity) {
                    return entity->objtype != entityType;
                }),
            entities.end());
        
        return entities;
    }

    void SpatialPartitioningSystem::resetStatistics()
    {
        queryCount_ = 0;
        updateCount_ = 0;
        totalQueryTime_ = 0.0;
        averageQueryTime_ = 0.0;
    }

    auto SpatialPartitioningSystem::getEntityPosition(CBaseEntity* entity) const -> Position3D
    {
        if (!entity)
        {
            return Position3D();
        }
        
        // Get position from entity's location data
        return Position3D(entity->loc.p.x, entity->loc.p.y, entity->loc.p.z);
    }

    void SpatialPartitioningSystem::updatePerformanceStats(double queryTime) const
    {
        totalQueryTime_ += queryTime;
        if (queryCount_ > 0)
        {
            averageQueryTime_ = totalQueryTime_ / queryCount_;
        }
    }

    // SpatialGrid implementation
    SpatialGrid::SpatialGrid(const AABB& bounds, float cellSize)
    : bounds_(bounds)
    , cellSize_(cellSize)
    {
        TracyZoneScoped;
        
        const float width = bounds_.max.x - bounds_.min.x;
        const float height = bounds_.max.y - bounds_.min.y;
        const float depth = bounds_.max.z - bounds_.min.z;
        
        gridWidth_ = static_cast<size_t>(std::ceil(width / cellSize_)) + 1;
        gridHeight_ = static_cast<size_t>(std::ceil(height / cellSize_)) + 1;
        gridDepth_ = static_cast<size_t>(std::ceil(depth / cellSize_)) + 1;
        
        cells_.resize(gridWidth_ * gridHeight_ * gridDepth_);
        
        ShowInfo("SpatialGrid: Initialized %zux%zux%zu grid (cell size: %.1f)", 
                 gridWidth_, gridHeight_, gridDepth_, cellSize_);
    }

    SpatialGrid::~SpatialGrid()
    {
        TracyZoneScoped;
    }

    void SpatialGrid::addEntity(CBaseEntity* entity, const Position3D& position)
    {
        TracyZoneScoped;
        
        if (!entity)
        {
            return;
        }
        
        const size_t cellIndex = getCellIndex(position);
        if (cellIndex < cells_.size())
        {
            cells_[cellIndex].entities.push_back(entity);
        }
    }

    void SpatialGrid::removeEntity(CBaseEntity* entity, const Position3D& position)
    {
        TracyZoneScoped;
        
        if (!entity)
        {
            return;
        }
        
        const size_t cellIndex = getCellIndex(position);
        if (cellIndex < cells_.size())
        {
            auto& cell = cells_[cellIndex];
            cell.entities.erase(
                std::remove(cell.entities.begin(), cell.entities.end(), entity),
                cell.entities.end());
        }
    }

    void SpatialGrid::updateEntity(CBaseEntity* entity, const Position3D& oldPos, const Position3D& newPos)
    {
        TracyZoneScoped;
        
        const size_t oldIndex = getCellIndex(oldPos);
        const size_t newIndex = getCellIndex(newPos);
        
        if (oldIndex != newIndex)
        {
            removeEntity(entity, oldPos);
            addEntity(entity, newPos);
        }
    }

    auto SpatialGrid::queryRange(const AABB& queryBounds) const -> std::vector<CBaseEntity*>
    {
        TracyZoneScoped;
        
        std::vector<CBaseEntity*> results;
        
        // Calculate grid cell range for query bounds
        const size_t minX = static_cast<size_t>(std::max(0.0f, (queryBounds.min.x - bounds_.min.x) / cellSize_));
        const size_t maxX = static_cast<size_t>(std::min(static_cast<float>(gridWidth_ - 1), (queryBounds.max.x - bounds_.min.x) / cellSize_));
        const size_t minY = static_cast<size_t>(std::max(0.0f, (queryBounds.min.y - bounds_.min.y) / cellSize_));
        const size_t maxY = static_cast<size_t>(std::min(static_cast<float>(gridHeight_ - 1), (queryBounds.max.y - bounds_.min.y) / cellSize_));
        const size_t minZ = static_cast<size_t>(std::max(0.0f, (queryBounds.min.z - bounds_.min.z) / cellSize_));
        const size_t maxZ = static_cast<size_t>(std::min(static_cast<float>(gridDepth_ - 1), (queryBounds.max.z - bounds_.min.z) / cellSize_));
        
        for (size_t x = minX; x <= maxX; ++x)
        {
            for (size_t y = minY; y <= maxY; ++y)
            {
                for (size_t z = minZ; z <= maxZ; ++z)
                {
                    if (isValidCell(x, y, z))
                    {
                        const size_t cellIndex = x + y * gridWidth_ + z * gridWidth_ * gridHeight_;
                        const auto& cell = cells_[cellIndex];
                        
                        for (auto* entity : cell.entities)
                        {
                            if (entity)
                            {
                                results.push_back(entity);
                            }
                        }
                    }
                }
            }
        }
        
        return results;
    }

    auto SpatialGrid::queryRadius(const Position3D& center, float radius) const -> std::vector<CBaseEntity*>
    {
        TracyZoneScoped;
        
        // Create AABB for radius and query
        const AABB radiusBounds(
            Position3D(center.x - radius, center.y - radius, center.z - radius),
            Position3D(center.x + radius, center.y + radius, center.z + radius)
        );
        
        auto results = queryRange(radiusBounds);
        
        // Filter by actual distance
        const float radiusSquared = radius * radius;
        results.erase(
            std::remove_if(results.begin(), results.end(),
                [&center, radiusSquared](CBaseEntity* entity) {
                    if (!entity) return true;
                    const Position3D entityPos(entity->loc.p.x, entity->loc.p.y, entity->loc.p.z);
                    return entityPos.distanceSquared(center) > radiusSquared;
                }),
            results.end());
        
        return results;
    }

    auto SpatialGrid::getCellIndex(const Position3D& position) const -> size_t
    {
        const size_t x = static_cast<size_t>(std::max(0.0f, std::min(static_cast<float>(gridWidth_ - 1), (position.x - bounds_.min.x) / cellSize_)));
        const size_t y = static_cast<size_t>(std::max(0.0f, std::min(static_cast<float>(gridHeight_ - 1), (position.y - bounds_.min.y) / cellSize_)));
        const size_t z = static_cast<size_t>(std::max(0.0f, std::min(static_cast<float>(gridDepth_ - 1), (position.z - bounds_.min.z) / cellSize_)));
        
        return x + y * gridWidth_ + z * gridWidth_ * gridHeight_;
    }

    auto SpatialGrid::isValidCell(size_t x, size_t y, size_t z) const -> bool
    {
        return x < gridWidth_ && y < gridHeight_ && z < gridDepth_;
    }

    // Global system functions
    auto getSpatialSystem() -> SpatialPartitioningSystem&
    {
        if (!g_spatialSystem)
        {
            g_spatialSystem = std::make_unique<SpatialPartitioningSystem>();
        }
        return *g_spatialSystem;
    }

    void initializeSpatialSystem(const AABB& worldBounds)
    {
        getSpatialSystem().initialize(worldBounds);
    }

    void shutdownSpatialSystem()
    {
        if (g_spatialSystem)
        {
            g_spatialSystem->shutdown();
            g_spatialSystem.reset();
        }
    }

} // namespace spatial