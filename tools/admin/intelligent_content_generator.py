#!/usr/bin/env python3
"""
FFXI-Server Intelligent Content Generation - Iteration 13
=========================================================

AI-generated quests and storylines, procedural content generation with quality control,
dynamic economy balancing and optimization, and automated testing and quality assurance.

Part of: Iteration 13 - Advanced AI & Automation
Timeline: Q2 2025 Implementation
Status: Core intelligent content generation framework
"""

import os
import sys
import json
import time
import random
import sqlite3
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re
import statistics

class ContentType(Enum):
    """Types of content that can be generated."""
    QUEST = "quest"
    STORYLINE = "storyline"
    DIALOGUE = "dialogue"
    ITEM = "item"
    MONSTER = "monster"
    DUNGEON = "dungeon"
    EVENT = "event"
    ECONOMY_ADJUSTMENT = "economy_adjustment"

class QualityLevel(Enum):
    """Quality levels for generated content."""
    PROTOTYPE = 1
    DRAFT = 2
    GOOD = 3
    HIGH = 4
    EXCEPTIONAL = 5

class ContentTheme(Enum):
    """Themes for content generation."""
    ADVENTURE = "adventure"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    TRAGEDY = "tragedy"
    COMEDY = "comedy"
    HORROR = "horror"
    EPIC = "epic"
    SLICE_OF_LIFE = "slice_of_life"

@dataclass
class ContentTemplate:
    """Template for generating content."""
    template_id: str
    content_type: ContentType
    theme: ContentTheme
    structure: Dict[str, Any]
    variables: List[str]
    quality_metrics: Dict[str, float]
    usage_count: int
    success_rate: float

@dataclass
class GeneratedContent:
    """Generated content item."""
    content_id: str
    content_type: ContentType
    title: str
    description: str
    content_data: Dict[str, Any]
    theme: ContentTheme
    quality_score: float
    generation_time: datetime
    template_id: str
    target_audience: Dict[str, Any]
    validation_status: str
    feedback_scores: List[float]

@dataclass
class EconomyItem:
    """Economy item for dynamic balancing."""
    item_id: str
    item_name: str
    current_price: float
    base_price: float
    supply: int
    demand: int
    price_history: List[Tuple[datetime, float]]
    volatility: float
    market_trend: str

@dataclass
class QuestGeneration:
    """Quest generation parameters."""
    quest_type: str
    difficulty_level: int
    target_level_range: Tuple[int, int]
    required_jobs: List[str]
    location: str
    rewards: Dict[str, Any]
    prerequisites: List[str]
    estimated_duration: int
    storyline_connection: Optional[str]

class IntelligentContentGenerator:
    """Intelligent content generation system with AI and quality control."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.db_path = Path(__file__).parent / "content_generation.db"
        self.templates_path = Path(__file__).parent / "content_templates"
        self.templates_path.mkdir(exist_ok=True)
        self.running = False
        self.threads = []
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('content_generation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        # Content generation components
        self.content_templates = {}
        self.story_elements = []
        self.character_archetypes = []
        self.location_database = []
        self.item_templates = []
        
        # Economy tracking
        self.economy_items = {}
        self.price_history = {}
        
        # Quality control
        self.quality_thresholds = {
            'narrative_coherence': 0.7,
            'gameplay_balance': 0.8,
            'technical_feasibility': 0.9,
            'player_engagement': 0.6,
            'content_originality': 0.5
        }
        
        # Load initial data
        self._load_templates()
        self._load_story_database()
        self._load_economy_data()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load content generation configuration."""
        default_config = {
            'generation_interval': 600,          # 10 minutes
            'economy_analysis_interval': 1800,   # 30 minutes
            'quality_control_enabled': True,
            'auto_approve_threshold': 0.8,
            'max_content_per_cycle': 5,
            'storyline_coherence_weight': 0.8,
            'player_feedback_weight': 0.6,
            'economy_stability_target': 0.1,    # 10% price variation
            'content_diversity_requirement': 0.7,
            'automated_testing_enabled': True,
            'content_retention_days': 90,
            'min_quality_score': 0.6
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _init_database(self):
        """Initialize SQLite database for content generation."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS content_templates (
                    template_id TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    structure TEXT NOT NULL,
                    variables TEXT,
                    quality_metrics TEXT,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS generated_content (
                    content_id TEXT PRIMARY KEY,
                    content_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    content_data TEXT,
                    theme TEXT,
                    quality_score REAL,
                    generation_time DATETIME,
                    template_id TEXT,
                    target_audience TEXT,
                    validation_status TEXT DEFAULT 'pending',
                    feedback_scores TEXT,
                    approved BOOLEAN DEFAULT FALSE,
                    deployed BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS economy_items (
                    item_id TEXT PRIMARY KEY,
                    item_name TEXT NOT NULL,
                    current_price REAL,
                    base_price REAL,
                    supply INTEGER,
                    demand INTEGER,
                    price_history TEXT,
                    volatility REAL,
                    market_trend TEXT,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS story_elements (
                    element_id TEXT PRIMARY KEY,
                    element_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    theme TEXT,
                    usage_count INTEGER DEFAULT 0,
                    quality_rating REAL DEFAULT 0.5,
                    connections TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS quest_chains (
                    chain_id TEXT PRIMARY KEY,
                    chain_name TEXT NOT NULL,
                    quest_ids TEXT,
                    storyline_theme TEXT,
                    target_level_range TEXT,
                    progression_requirements TEXT,
                    completion_rate REAL DEFAULT 0.0,
                    player_rating REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS content_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    player_id INTEGER,
                    feedback_type TEXT,
                    rating REAL,
                    comments TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS quality_tests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    test_result TEXT,
                    pass_fail BOOLEAN,
                    score REAL,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS economy_adjustments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjustment_type TEXT NOT NULL,
                    target_items TEXT,
                    old_values TEXT,
                    new_values TEXT,
                    reason TEXT,
                    impact_score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_content_type_quality 
                ON generated_content(content_type, quality_score);
                CREATE INDEX IF NOT EXISTS idx_economy_last_updated 
                ON economy_items(last_updated);
                CREATE INDEX IF NOT EXISTS idx_feedback_content 
                ON content_feedback(content_id, timestamp);
            """)
    
    def _load_templates(self):
        """Load content generation templates."""
        # Quest templates
        quest_templates = {
            'fetch_quest': {
                'structure': {
                    'objective': 'Collect {item_count} {item_name} from {location}',
                    'giver': '{npc_name} in {starting_location}',
                    'reward': '{reward_type}: {reward_amount}',
                    'difficulty_factors': ['item_rarity', 'location_danger', 'item_count']
                },
                'variables': ['item_count', 'item_name', 'location', 'npc_name', 'starting_location', 'reward_type', 'reward_amount'],
                'quality_metrics': {
                    'narrative_coherence': 0.6,
                    'gameplay_balance': 0.8,
                    'player_engagement': 0.5
                }
            },
            'escort_quest': {
                'structure': {
                    'objective': 'Safely escort {npc_name} from {start_location} to {end_location}',
                    'challenges': ['monster_encounters', 'environmental_hazards', 'time_limits'],
                    'reward': '{reward_type}: {reward_amount}',
                    'special_conditions': ['npc_abilities', 'route_variations']
                },
                'variables': ['npc_name', 'start_location', 'end_location', 'reward_type', 'reward_amount'],
                'quality_metrics': {
                    'narrative_coherence': 0.7,
                    'gameplay_balance': 0.7,
                    'player_engagement': 0.8
                }
            },
            'mystery_quest': {
                'structure': {
                    'objective': 'Investigate {mystery_subject} in {location}',
                    'clues': ['witness_accounts', 'physical_evidence', 'hidden_messages'],
                    'revelation': '{mystery_solution}',
                    'reward': '{reward_type}: {reward_amount}'
                },
                'variables': ['mystery_subject', 'location', 'mystery_solution', 'reward_type', 'reward_amount'],
                'quality_metrics': {
                    'narrative_coherence': 0.9,
                    'gameplay_balance': 0.6,
                    'player_engagement': 0.9
                }
            }
        }
        
        # Store templates in database
        with sqlite3.connect(self.db_path) as conn:
            for template_id, template_data in quest_templates.items():
                template = ContentTemplate(
                    template_id=template_id,
                    content_type=ContentType.QUEST,
                    theme=ContentTheme.ADVENTURE,
                    structure=template_data['structure'],
                    variables=template_data['variables'],
                    quality_metrics=template_data['quality_metrics'],
                    usage_count=0,
                    success_rate=0.0
                )
                
                self.content_templates[template_id] = template
                
                conn.execute("""
                    INSERT OR REPLACE INTO content_templates 
                    (template_id, content_type, theme, structure, variables, quality_metrics)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    template.template_id,
                    template.content_type.value,
                    template.theme.value,
                    json.dumps(template.structure),
                    json.dumps(template.variables),
                    json.dumps(template.quality_metrics)
                ))
        
        self.logger.info(f"Loaded {len(quest_templates)} content templates")
    
    def _load_story_database(self):
        """Load story elements database."""
        story_elements = [
            {'type': 'character', 'content': 'mysterious merchant', 'theme': 'mystery'},
            {'type': 'character', 'content': 'brave knight', 'theme': 'adventure'},
            {'type': 'character', 'content': 'wise elder', 'theme': 'epic'},
            {'type': 'character', 'content': 'cunning thief', 'theme': 'adventure'},
            {'type': 'location', 'content': 'ancient ruins', 'theme': 'mystery'},
            {'type': 'location', 'content': 'bustling marketplace', 'theme': 'slice_of_life'},
            {'type': 'location', 'content': 'dark forest', 'theme': 'horror'},
            {'type': 'location', 'content': 'mountain peak', 'theme': 'adventure'},
            {'type': 'item', 'content': 'magical artifact', 'theme': 'epic'},
            {'type': 'item', 'content': 'lost heirloom', 'theme': 'mystery'},
            {'type': 'item', 'content': 'rare herb', 'theme': 'adventure'},
            {'type': 'conflict', 'content': 'ancient curse', 'theme': 'horror'},
            {'type': 'conflict', 'content': 'political intrigue', 'theme': 'mystery'},
            {'type': 'conflict', 'content': 'monster invasion', 'theme': 'adventure'},
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for element in story_elements:
                element_id = hashlib.md5(f"{element['type']}_{element['content']}".encode()).hexdigest()
                conn.execute("""
                    INSERT OR IGNORE INTO story_elements 
                    (element_id, element_type, content, theme)
                    VALUES (?, ?, ?, ?)
                """, (element_id, element['type'], element['content'], element['theme']))
        
        self.logger.info(f"Loaded {len(story_elements)} story elements")
    
    def _load_economy_data(self):
        """Load economy data for dynamic balancing."""
        # Mock economy items
        items = [
            {'id': 'copper_ore', 'name': 'Copper Ore', 'base_price': 100, 'supply': 1000, 'demand': 800},
            {'id': 'iron_sword', 'name': 'Iron Sword', 'base_price': 500, 'supply': 200, 'demand': 250},
            {'id': 'health_potion', 'name': 'Health Potion', 'base_price': 50, 'supply': 2000, 'demand': 1800},
            {'id': 'magic_crystal', 'name': 'Magic Crystal', 'base_price': 1000, 'supply': 50, 'demand': 80},
            {'id': 'leather_boots', 'name': 'Leather Boots', 'base_price': 200, 'supply': 300, 'demand': 280},
        ]
        
        for item in items:
            # Calculate current price based on supply/demand
            supply_demand_ratio = item['supply'] / max(1, item['demand'])
            price_modifier = 1.0 / supply_demand_ratio if supply_demand_ratio > 0 else 1.0
            current_price = item['base_price'] * price_modifier
            
            economy_item = EconomyItem(
                item_id=item['id'],
                item_name=item['name'],
                current_price=current_price,
                base_price=item['base_price'],
                supply=item['supply'],
                demand=item['demand'],
                price_history=[(datetime.now(), current_price)],
                volatility=0.1,
                market_trend='stable'
            )
            
            self.economy_items[item['id']] = economy_item
        
        self.logger.info(f"Loaded {len(items)} economy items")
    
    def generate_quest(self, template_id: str, target_level: int, theme: Optional[ContentTheme] = None) -> Optional[GeneratedContent]:
        """Generate a quest using specified template."""
        try:
            if template_id not in self.content_templates:
                self.logger.error(f"Template {template_id} not found")
                return None
            
            template = self.content_templates[template_id]
            
            # Generate variable values
            variables = self._generate_quest_variables(template, target_level, theme)
            
            # Fill template
            quest_data = self._fill_template(template, variables)
            
            # Calculate quality score
            quality_score = self._calculate_content_quality(quest_data, template)
            
            # Create generated content
            content_id = f"quest_{template_id}_{int(time.time())}_{random.randint(1000, 9999)}"
            
            generated_content = GeneratedContent(
                content_id=content_id,
                content_type=ContentType.QUEST,
                title=quest_data.get('title', f"Generated Quest: {template_id}"),
                description=quest_data.get('description', ''),
                content_data=quest_data,
                theme=theme or template.theme,
                quality_score=quality_score,
                generation_time=datetime.now(),
                template_id=template_id,
                target_audience={'min_level': target_level, 'max_level': target_level + 5},
                validation_status='pending',
                feedback_scores=[]
            )
            
            # Store in database
            self._store_generated_content(generated_content)
            
            # Update template usage
            template.usage_count += 1
            
            self.logger.info(f"Generated quest: {generated_content.title} (Quality: {quality_score:.2f})")
            return generated_content
            
        except Exception as e:
            self.logger.error(f"Quest generation failed: {e}")
            return None
    
    def _generate_quest_variables(self, template: ContentTemplate, target_level: int, theme: Optional[ContentTheme]) -> Dict[str, str]:
        """Generate variable values for quest template."""
        variables = {}
        
        # Level-appropriate content
        level_tier = self._get_level_tier(target_level)
        
        for var in template.variables:
            if var == 'item_count':
                variables[var] = str(random.randint(1, min(10, max(1, target_level // 10))))
            elif var == 'item_name':
                variables[var] = self._select_level_appropriate_item(level_tier)
            elif var == 'location':
                variables[var] = self._select_level_appropriate_location(level_tier)
            elif var == 'npc_name':
                variables[var] = self._generate_npc_name()
            elif var == 'starting_location':
                variables[var] = self._select_safe_location(level_tier)
            elif var == 'end_location':
                variables[var] = self._select_level_appropriate_location(level_tier)
            elif var == 'reward_type':
                variables[var] = random.choice(['experience', 'gil', 'item'])
            elif var == 'reward_amount':
                if variables.get('reward_type') == 'experience':
                    variables[var] = str(target_level * random.randint(50, 150))
                elif variables.get('reward_type') == 'gil':
                    variables[var] = str(target_level * random.randint(10, 50))
                else:
                    variables[var] = self._select_level_appropriate_item(level_tier)
            elif var == 'mystery_subject':
                variables[var] = random.choice(['disappearing villagers', 'strange lights', 'ancient prophecy', 'missing caravan'])
            elif var == 'mystery_solution':
                variables[var] = random.choice(['hidden cult', 'magical disturbance', 'monster nest', 'bandit hideout'])
            else:
                variables[var] = f"generated_{var}"
        
        return variables
    
    def _get_level_tier(self, level: int) -> str:
        """Get level tier for content generation."""
        if level <= 10:
            return 'beginner'
        elif level <= 30:
            return 'intermediate'
        elif level <= 50:
            return 'advanced'
        elif level <= 70:
            return 'expert'
        else:
            return 'master'
    
    def _select_level_appropriate_item(self, level_tier: str) -> str:
        """Select appropriate item for level tier."""
        items_by_tier = {
            'beginner': ['copper ore', 'rabbit hide', 'wooden stick', 'small potion'],
            'intermediate': ['iron ore', 'wolf pelt', 'steel dagger', 'health potion'],
            'advanced': ['mithril ore', 'drake scale', 'enchanted sword', 'mana potion'],
            'expert': ['adamantite ore', 'dragon scale', 'legendary weapon', 'elixir'],
            'master': ['orichalcum ore', 'ancient artifact', 'divine weapon', 'panacea']
        }
        return random.choice(items_by_tier.get(level_tier, items_by_tier['intermediate']))
    
    def _select_level_appropriate_location(self, level_tier: str) -> str:
        """Select appropriate location for level tier."""
        locations_by_tier = {
            'beginner': ['West Ronfaure', 'East Sarutabaruta', 'South Gustaberg', 'nearby fields'],
            'intermediate': ['La Theine Plateau', 'Tahrongi Canyon', 'Konschtat Highlands', 'ancient ruins'],
            'advanced': ['Xarcabard', 'Beaucedine Glacier', 'Fei\'Yin', 'forgotten temple'],
            'expert': ['Tu\'Lia', 'Ru\'Aun Gardens', 'Ve\'Lugannon Palace', 'celestial nexus'],
            'master': ['Al\'Taieu', 'Grand Palace of Hu\'Xzoi', 'The Garden of Ru\'Hmet', 'dimensional rift']
        }
        return random.choice(locations_by_tier.get(level_tier, locations_by_tier['intermediate']))
    
    def _select_safe_location(self, level_tier: str) -> str:
        """Select safe starting location."""
        safe_locations = {
            'beginner': ['San d\'Oria', 'Bastok', 'Windurst'],
            'intermediate': ['Jeuno', 'Selbina', 'Mhaura'],
            'advanced': ['Kazham', 'Norg', 'Rabao'],
            'expert': ['Aht Urhgan Whitegate', 'Nashmau', 'Al Zahbi'],
            'master': ['Adoulin', 'Celennia Memorial Library', 'Mog Garden']
        }
        return random.choice(safe_locations.get(level_tier, safe_locations['intermediate']))
    
    def _generate_npc_name(self) -> str:
        """Generate NPC name."""
        first_names = ['Aldo', 'Brynn', 'Cera', 'Dain', 'Enna', 'Finn', 'Gora', 'Hal', 'Iris', 'Jax']
        last_names = ['Brightblade', 'Stormwind', 'Ironforge', 'Goldleaf', 'Moonwhisper', 'Stargazer']
        return f"{random.choice(first_names)} {random.choice(last_names)}"
    
    def _fill_template(self, template: ContentTemplate, variables: Dict[str, str]) -> Dict[str, Any]:
        """Fill template with generated variables."""
        filled_data = {}
        
        # Fill structure
        for key, value in template.structure.items():
            if isinstance(value, str):
                filled_value = value
                for var, replacement in variables.items():
                    filled_value = filled_value.replace(f"{{{var}}}", replacement)
                filled_data[key] = filled_value
            else:
                filled_data[key] = value
        
        # Generate title and description
        if 'objective' in filled_data:
            filled_data['title'] = f"Quest: {filled_data['objective']}"
            filled_data['description'] = f"A quest that requires you to {filled_data['objective'].lower()}."
        
        filled_data['variables_used'] = variables
        filled_data['generation_metadata'] = {
            'template_id': template.template_id,
            'generation_time': datetime.now().isoformat(),
            'quality_target': template.quality_metrics
        }
        
        return filled_data
    
    def _calculate_content_quality(self, content_data: Dict[str, Any], template: ContentTemplate) -> float:
        """Calculate quality score for generated content."""
        quality_score = 0.0
        weights = {
            'narrative_coherence': 0.3,
            'gameplay_balance': 0.3,
            'technical_feasibility': 0.2,
            'content_originality': 0.2
        }
        
        # Narrative coherence
        narrative_score = self._assess_narrative_coherence(content_data)
        quality_score += narrative_score * weights['narrative_coherence']
        
        # Gameplay balance
        balance_score = self._assess_gameplay_balance(content_data)
        quality_score += balance_score * weights['gameplay_balance']
        
        # Technical feasibility
        feasibility_score = self._assess_technical_feasibility(content_data)
        quality_score += feasibility_score * weights['technical_feasibility']
        
        # Content originality
        originality_score = self._assess_content_originality(content_data, template)
        quality_score += originality_score * weights['content_originality']
        
        return min(1.0, max(0.0, quality_score))
    
    def _assess_narrative_coherence(self, content_data: Dict[str, Any]) -> float:
        """Assess narrative coherence of content."""
        score = 0.5  # Base score
        
        # Check for logical consistency
        if 'objective' in content_data and 'reward' in content_data:
            score += 0.2
        
        # Check for appropriate complexity
        if 'description' in content_data and len(content_data['description']) > 20:
            score += 0.2
        
        # Check for story elements
        if 'giver' in content_data or 'challenges' in content_data:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_gameplay_balance(self, content_data: Dict[str, Any]) -> float:
        """Assess gameplay balance of content."""
        score = 0.6  # Base score
        
        # Check reward appropriateness
        if 'reward' in content_data:
            score += 0.2
        
        # Check difficulty scaling
        if 'difficulty_factors' in content_data:
            score += 0.1
        
        # Check for variety
        if 'challenges' in content_data or 'special_conditions' in content_data:
            score += 0.1
        
        return min(1.0, score)
    
    def _assess_technical_feasibility(self, content_data: Dict[str, Any]) -> float:
        """Assess technical feasibility of content."""
        # For demonstration, assume high feasibility for template-based content
        return 0.9
    
    def _assess_content_originality(self, content_data: Dict[str, Any], template: ContentTemplate) -> float:
        """Assess originality of generated content."""
        # Base originality inversely related to template usage
        base_score = max(0.3, 1.0 - (template.usage_count * 0.1))
        
        # Bonus for unique variable combinations
        variables = content_data.get('variables_used', {})
        unique_combinations = len(set(variables.values()))
        originality_bonus = min(0.3, unique_combinations * 0.05)
        
        return min(1.0, base_score + originality_bonus)
    
    def _store_generated_content(self, content: GeneratedContent):
        """Store generated content in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO generated_content 
                (content_id, content_type, title, description, content_data,
                 theme, quality_score, generation_time, template_id, target_audience,
                 validation_status, feedback_scores)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content.content_id,
                content.content_type.value,
                content.title,
                content.description,
                json.dumps(content.content_data, default=str),
                content.theme.value,
                content.quality_score,
                content.generation_time.isoformat(),
                content.template_id,
                json.dumps(content.target_audience),
                content.validation_status,
                json.dumps(content.feedback_scores)
            ))
    
    def analyze_economy_trends(self):
        """Analyze economy trends and suggest adjustments."""
        try:
            self.logger.info("Analyzing economy trends")
            
            adjustments_made = []
            
            for item_id, item in self.economy_items.items():
                # Calculate price volatility
                if len(item.price_history) > 5:
                    recent_prices = [price for _, price in item.price_history[-5:]]
                    volatility = statistics.stdev(recent_prices) / statistics.mean(recent_prices)
                    item.volatility = volatility
                
                # Detect price imbalances
                supply_demand_ratio = item.supply / max(1, item.demand)
                ideal_price = item.base_price
                
                if supply_demand_ratio > 2.0:  # Oversupply
                    # Suggest price reduction or supply limitation
                    suggested_price = item.current_price * 0.9
                    adjustment = self._create_economy_adjustment(
                        item_id, 'price_reduction', item.current_price, suggested_price,
                        f"Oversupply detected (ratio: {supply_demand_ratio:.2f})"
                    )
                    adjustments_made.append(adjustment)
                    
                elif supply_demand_ratio < 0.5:  # High demand
                    # Suggest price increase or supply boost
                    suggested_price = item.current_price * 1.1
                    adjustment = self._create_economy_adjustment(
                        item_id, 'price_increase', item.current_price, suggested_price,
                        f"High demand detected (ratio: {supply_demand_ratio:.2f})"
                    )
                    adjustments_made.append(adjustment)
                
                # Update price history
                item.price_history.append((datetime.now(), item.current_price))
                if len(item.price_history) > 100:  # Keep last 100 records
                    item.price_history.pop(0)
            
            self.logger.info(f"Generated {len(adjustments_made)} economy adjustments")
            return adjustments_made
            
        except Exception as e:
            self.logger.error(f"Economy analysis failed: {e}")
            return []
    
    def _create_economy_adjustment(self, item_id: str, adjustment_type: str, old_value: float, new_value: float, reason: str) -> Dict:
        """Create economy adjustment record."""
        adjustment = {
            'id': f"adj_{item_id}_{int(time.time())}",
            'adjustment_type': adjustment_type,
            'target_item': item_id,
            'old_value': old_value,
            'new_value': new_value,
            'reason': reason,
            'impact_score': abs(new_value - old_value) / old_value,
            'timestamp': datetime.now()
        }
        
        # Store in database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO economy_adjustments 
                (adjustment_type, target_items, old_values, new_values, reason, impact_score)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                adjustment_type,
                json.dumps([item_id]),
                json.dumps({'price': old_value}),
                json.dumps({'price': new_value}),
                reason,
                adjustment['impact_score']
            ))
        
        return adjustment
    
    def perform_quality_testing(self, content_id: str) -> Dict[str, Any]:
        """Perform automated quality testing on generated content."""
        try:
            # Load content
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("""
                    SELECT content_data, content_type FROM generated_content 
                    WHERE content_id = ?
                """, (content_id,)).fetchone()
                
                if not row:
                    return {'error': 'Content not found'}
                
                content_data = json.loads(row[0])
                content_type = row[1]
            
            test_results = {}
            
            # Narrative coherence test
            narrative_test = self._test_narrative_coherence(content_data)
            test_results['narrative_coherence'] = narrative_test
            
            # Gameplay balance test
            balance_test = self._test_gameplay_balance(content_data, content_type)
            test_results['gameplay_balance'] = balance_test
            
            # Technical feasibility test
            feasibility_test = self._test_technical_feasibility(content_data)
            test_results['technical_feasibility'] = feasibility_test
            
            # Player engagement test
            engagement_test = self._test_player_engagement(content_data)
            test_results['player_engagement'] = engagement_test
            
            # Calculate overall pass/fail
            overall_score = sum(test['score'] for test in test_results.values()) / len(test_results)
            overall_pass = overall_score >= self.config['min_quality_score']
            
            # Store test results
            for test_type, result in test_results.items():
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO quality_tests 
                        (content_id, test_type, test_result, pass_fail, score, details)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        content_id, test_type, result['result'],
                        result['pass'], result['score'], json.dumps(result['details'])
                    ))
            
            return {
                'content_id': content_id,
                'overall_score': overall_score,
                'overall_pass': overall_pass,
                'test_results': test_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Quality testing failed for {content_id}: {e}")
            return {'error': str(e)}
    
    def _test_narrative_coherence(self, content_data: Dict[str, Any]) -> Dict:
        """Test narrative coherence of content."""
        score = 0.0
        details = []
        
        # Check for required narrative elements
        if 'objective' in content_data:
            score += 0.3
            details.append("Has clear objective")
        
        if 'description' in content_data and len(content_data['description']) > 10:
            score += 0.2
            details.append("Has adequate description")
        
        # Check for logical consistency
        if 'giver' in content_data and 'reward' in content_data:
            score += 0.3
            details.append("Logical quest structure")
        
        # Check for engaging elements
        if any(key in content_data for key in ['challenges', 'mystery_subject', 'special_conditions']):
            score += 0.2
            details.append("Contains engaging elements")
        
        return {
            'score': min(1.0, score),
            'pass': score >= self.quality_thresholds['narrative_coherence'],
            'result': 'pass' if score >= self.quality_thresholds['narrative_coherence'] else 'fail',
            'details': details
        }
    
    def _test_gameplay_balance(self, content_data: Dict[str, Any], content_type: str) -> Dict:
        """Test gameplay balance of content."""
        score = 0.7  # Base score for template-based content
        details = ["Template-based generation provides baseline balance"]
        
        # Check reward appropriateness
        if 'reward' in content_data:
            score += 0.2
            details.append("Reward system present")
        
        # Check difficulty scaling
        if 'target_audience' in content_data:
            score += 0.1
            details.append("Level-appropriate content")
        
        return {
            'score': min(1.0, score),
            'pass': score >= self.quality_thresholds['gameplay_balance'],
            'result': 'pass' if score >= self.quality_thresholds['gameplay_balance'] else 'fail',
            'details': details
        }
    
    def _test_technical_feasibility(self, content_data: Dict[str, Any]) -> Dict:
        """Test technical feasibility of content."""
        score = 0.9  # High score for template-based content
        details = ["Template-based content has high technical feasibility"]
        
        # Check for complex requirements
        if 'special_conditions' in content_data:
            score -= 0.1
            details.append("Special conditions may require additional implementation")
        
        return {
            'score': score,
            'pass': score >= self.quality_thresholds['technical_feasibility'],
            'result': 'pass' if score >= self.quality_thresholds['technical_feasibility'] else 'fail',
            'details': details
        }
    
    def _test_player_engagement(self, content_data: Dict[str, Any]) -> Dict:
        """Test player engagement potential of content."""
        score = 0.5  # Base score
        details = []
        
        # Check for variety
        if 'challenges' in content_data:
            score += 0.2
            details.append("Multiple challenges increase engagement")
        
        # Check for story elements
        if any(key in content_data for key in ['mystery_subject', 'revelation', 'giver']):
            score += 0.2
            details.append("Story elements enhance engagement")
        
        # Check for player choice
        if 'special_conditions' in content_data:
            score += 0.1
            details.append("Special conditions provide choice")
        
        return {
            'score': min(1.0, score),
            'pass': score >= self.quality_thresholds['player_engagement'],
            'result': 'pass' if score >= self.quality_thresholds['player_engagement'] else 'fail',
            'details': details
        }
    
    def content_generation_loop(self):
        """Main content generation loop."""
        while self.running:
            try:
                # Generate new content
                for i in range(self.config['max_content_per_cycle']):
                    # Select random template and parameters
                    template_id = random.choice(list(self.content_templates.keys()))
                    target_level = random.randint(1, 75)
                    theme = random.choice(list(ContentTheme))
                    
                    content = self.generate_quest(template_id, target_level, theme)
                    
                    if content and self.config['automated_testing_enabled']:
                        # Perform quality testing
                        test_results = self.perform_quality_testing(content.content_id)
                        
                        # Auto-approve high-quality content
                        if (test_results.get('overall_score', 0) >= self.config['auto_approve_threshold']):
                            self._approve_content(content.content_id)
                
                time.sleep(self.config['generation_interval'])
                
            except Exception as e:
                self.logger.error(f"Content generation loop error: {e}")
                time.sleep(300)
    
    def economy_analysis_loop(self):
        """Economy analysis and adjustment loop."""
        while self.running:
            try:
                self.analyze_economy_trends()
                time.sleep(self.config['economy_analysis_interval'])
            except Exception as e:
                self.logger.error(f"Economy analysis loop error: {e}")
                time.sleep(900)
    
    def _approve_content(self, content_id: str):
        """Approve content for deployment."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE generated_content 
                SET validation_status = 'approved', approved = TRUE
                WHERE content_id = ?
            """, (content_id,))
        
        self.logger.info(f"Auto-approved content: {content_id}")
    
    def start(self):
        """Start the intelligent content generation system."""
        if self.running:
            self.logger.warning("Content generation system already running")
            return
        
        self.running = True
        self.logger.info("Starting Intelligent Content Generation - Iteration 13")
        
        # Start processing threads
        threads = [
            threading.Thread(target=self.content_generation_loop),
            threading.Thread(target=self.economy_analysis_loop)
        ]
        
        for thread in threads:
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        self.logger.info("Intelligent Content Generation started successfully")
    
    def stop(self):
        """Stop the intelligent content generation system."""
        self.logger.info("Stopping Intelligent Content Generation")
        self.running = False
        
        for thread in self.threads:
            thread.join(timeout=5)
        
        self.logger.info("Intelligent Content Generation stopped")
    
    def get_status_report(self) -> Dict:
        """Generate comprehensive status report."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Content generation statistics
                content_stats = conn.execute("""
                    SELECT content_type, COUNT(*) as count, AVG(quality_score) as avg_quality
                    FROM generated_content 
                    WHERE generation_time > datetime('now', '-24 hours')
                    GROUP BY content_type
                """).fetchall()
                
                # Quality testing results
                quality_stats = conn.execute("""
                    SELECT test_type, AVG(score) as avg_score, 
                           SUM(CASE WHEN pass_fail THEN 1 ELSE 0 END) as pass_count,
                           COUNT(*) as total_count
                    FROM quality_tests 
                    WHERE timestamp > datetime('now', '-24 hours')
                    GROUP BY test_type
                """).fetchall()
                
                # Economy adjustments
                economy_stats = conn.execute("""
                    SELECT adjustment_type, COUNT(*) as count, AVG(impact_score) as avg_impact
                    FROM economy_adjustments 
                    WHERE timestamp > datetime('now', '-24 hours')
                    GROUP BY adjustment_type
                """).fetchall()
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': 'running' if self.running else 'stopped',
                    'templates_loaded': len(self.content_templates),
                    'economy_items_tracked': len(self.economy_items),
                    'content_generation_stats': content_stats,
                    'quality_testing_stats': quality_stats,
                    'economy_adjustment_stats': economy_stats,
                    'config': self.config
                }
        except Exception as e:
            self.logger.error(f"Status report generation failed: {e}")
            return {'error': str(e)}

def main():
    """Main entry point for intelligent content generation."""
    generator = IntelligentContentGenerator()
    
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == 'start':
                generator.start()
                while generator.running:
                    time.sleep(1)
            elif command == 'status':
                report = generator.get_status_report()
                print(json.dumps(report, indent=2, default=str))
            elif command == 'generate':
                if len(sys.argv) > 3:
                    template_id = sys.argv[2]
                    target_level = int(sys.argv[3])
                    content = generator.generate_quest(template_id, target_level)
                    if content:
                        print(json.dumps(asdict(content), indent=2, default=str))
                else:
                    print("Usage: intelligent_content_generator.py generate <template_id> <level>")
            elif command == 'test':
                if len(sys.argv) > 2:
                    content_id = sys.argv[2]
                    results = generator.perform_quality_testing(content_id)
                    print(json.dumps(results, indent=2, default=str))
                else:
                    print("Usage: intelligent_content_generator.py test <content_id>")
            else:
                print("Usage: intelligent_content_generator.py [start|status|generate|test]")
        else:
            generator.start()
            print("Intelligent Content Generation running. Press Ctrl+C to stop.")
            while generator.running:
                time.sleep(1)
    
    except KeyboardInterrupt:
        generator.stop()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()