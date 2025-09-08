#!/usr/bin/env python3
"""
AI-GM Machine Learning Engine
Cross-platform ML capabilities with GPU/NPU support for learning from server data
"""

import os
import sys
import logging
import platform
import subprocess
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import pickle

# Hardware detection and ML framework imports
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, Dataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier, IsolationForest
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import openvino as ov
    OPENVINO_AVAILABLE = True
except ImportError:
    OPENVINO_AVAILABLE = False

@dataclass
class HardwareInfo:
    """Information about available hardware acceleration"""
    platform: str
    cpu_cores: int
    has_cuda: bool = False
    has_rocm: bool = False
    has_metal: bool = False
    has_openvino: bool = False
    gpu_devices: List[str] = None
    npu_devices: List[str] = None
    recommended_backend: str = "cpu"

@dataclass
class PlayerBehaviorData:
    """Player behavior data for ML analysis"""
    player_id: int
    timestamp: datetime
    zone_id: int
    position: Tuple[float, float, float]
    hp_percentage: float
    mp_percentage: float
    job_level: int
    actions_per_minute: float
    chat_messages_per_hour: int
    login_duration_minutes: float
    death_count: int
    jail_history: int
    gm_interactions: int
    suspicious_score: float = 0.0

class AIGMMLEngine:
    """Main ML engine for AI-GM system"""
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger('AI-GM-ML')
        self.hardware_info = self._detect_hardware()
        self.models = {}
        self.scalers = {}
        self.data_cache = []
        self.learning_enabled = True
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize ML backend
        self._initialize_backend()
        
    def _detect_hardware(self) -> HardwareInfo:
        """Detect available hardware acceleration"""
        info = HardwareInfo(
            platform=platform.system(),
            cpu_cores=os.cpu_count() or 4,
            gpu_devices=[],
            npu_devices=[]
        )
        
        # Detect NVIDIA CUDA
        if TORCH_AVAILABLE:
            info.has_cuda = torch.cuda.is_available()
            if info.has_cuda:
                for i in range(torch.cuda.device_count()):
                    device_name = torch.cuda.get_device_name(i)
                    info.gpu_devices.append(f"CUDA:{i} - {device_name}")
                info.recommended_backend = "cuda"
        
        # Detect AMD ROCm
        try:
            if platform.system() == "Linux":
                result = subprocess.run(['rocm-smi'], capture_output=True, text=True)
                if result.returncode == 0:
                    info.has_rocm = True
                    info.gpu_devices.append("ROCm GPU")
                    if not info.has_cuda:  # Prefer CUDA if available
                        info.recommended_backend = "rocm"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # Detect Apple Metal (macOS)
        if platform.system() == "Darwin":
            try:
                if TF_AVAILABLE:
                    # Check for tensorflow-metal
                    import tensorflow_metal
                    info.has_metal = True
                    info.gpu_devices.append("Apple Metal GPU")
                    if not info.has_cuda:
                        info.recommended_backend = "metal"
            except ImportError:
                pass
        
        # Detect Intel OpenVINO/NPU
        if OPENVINO_AVAILABLE:
            try:
                core = ov.Core()
                devices = core.available_devices
                for device in devices:
                    if "NPU" in device:
                        info.has_openvino = True
                        info.npu_devices.append(f"Intel {device}")
                        if info.recommended_backend == "cpu":
                            info.recommended_backend = "openvino"
                    elif "GPU" in device and not info.gpu_devices:
                        info.gpu_devices.append(f"Intel {device}")
            except Exception:
                pass
        
        self.logger.info(f"Hardware detected: {info.platform}, {info.cpu_cores} CPU cores")
        self.logger.info(f"GPU devices: {info.gpu_devices}")
        self.logger.info(f"NPU devices: {info.npu_devices}")
        self.logger.info(f"Recommended backend: {info.recommended_backend}")
        
        return info
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load ML configuration"""
        default_config = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 100,
            "model_save_interval": 1000,  # Save every 1000 training samples
            "anomaly_threshold": 0.7,
            "behavior_window_hours": 24,
            "max_cache_size": 10000,
            "enable_real_time_learning": True,
            "model_types": ["isolation_forest", "neural_network", "random_forest"]
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _initialize_backend(self):
        """Initialize the ML backend based on available hardware"""
        try:
            if self.hardware_info.recommended_backend == "cuda" and TORCH_AVAILABLE:
                torch.backends.cudnn.benchmark = True
                self.device = torch.device("cuda")
                self.logger.info("Initialized CUDA backend")
                
            elif self.hardware_info.recommended_backend == "metal" and TF_AVAILABLE:
                # Configure TensorFlow for Metal
                tf.config.experimental.set_memory_growth(
                    tf.config.experimental.list_physical_devices('GPU')[0], True
                )
                self.device = "GPU"
                self.logger.info("Initialized Metal backend")
                
            elif self.hardware_info.recommended_backend == "openvino" and OPENVINO_AVAILABLE:
                self.ov_core = ov.Core()
                self.device = "NPU" if self.hardware_info.npu_devices else "GPU"
                self.logger.info("Initialized OpenVINO backend")
                
            else:
                self.device = "cpu"
                self.logger.info("Using CPU backend")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize preferred backend: {e}")
            self.device = "cpu"
    
    def preprocess_player_data(self, raw_data: List[Dict]) -> pd.DataFrame:
        """Preprocess raw player data for ML"""
        try:
            df = pd.DataFrame(raw_data)
            
            # Feature engineering
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['position_distance'] = np.sqrt(
                df['pos_x']**2 + df['pos_y']**2 + df['pos_z']**2
            )
            
            # Behavioral features
            df['login_frequency'] = df.groupby('player_id')['timestamp'].transform('count')
            df['zone_changes'] = df.groupby('player_id')['zone_id'].transform('nunique')
            df['avg_session_length'] = df.groupby('player_id')['login_duration_minutes'].transform('mean')
            
            # Risk indicators
            df['risk_score'] = (
                (df['death_count'] * 0.1) +
                (df['jail_history'] * 0.3) +
                (df['gm_interactions'] * 0.2) +
                (df['actions_per_minute'] < 0.1) * 0.4  # AFK indicator
            )
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            return pd.DataFrame()
    
    def train_anomaly_detector(self, training_data: pd.DataFrame):
        """Train anomaly detection model"""
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn not available, skipping anomaly detection training")
            return
        
        try:
            # Prepare features
            feature_columns = [
                'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                'login_frequency', 'zone_changes', 'avg_session_length', 'risk_score'
            ]
            
            X = training_data[feature_columns].fillna(0)
            
            # Scale features
            if 'anomaly_scaler' not in self.scalers:
                self.scalers['anomaly_scaler'] = StandardScaler()
                X_scaled = self.scalers['anomaly_scaler'].fit_transform(X)
            else:
                X_scaled = self.scalers['anomaly_scaler'].transform(X)
            
            # Train Isolation Forest
            self.models['isolation_forest'] = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            self.models['isolation_forest'].fit(X_scaled)
            
            self.logger.info("Anomaly detection model trained successfully")
            
        except Exception as e:
            self.logger.error(f"Error training anomaly detector: {e}")
    
    def train_behavior_classifier(self, training_data: pd.DataFrame):
        """Train behavior classification model"""
        if not SKLEARN_AVAILABLE:
            return
        
        try:
            # Create labels based on risk patterns
            training_data['behavior_label'] = pd.cut(
                training_data['risk_score'],
                bins=[0, 0.2, 0.5, 0.8, 1.0],
                labels=['normal', 'suspicious', 'concerning', 'violation']
            )
            
            feature_columns = [
                'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                'login_frequency', 'zone_changes', 'avg_session_length'
            ]
            
            X = training_data[feature_columns].fillna(0)
            y = training_data['behavior_label']
            
            # Remove NaN labels
            mask = ~y.isna()
            X = X[mask]
            y = y[mask]
            
            if len(X) < 10:  # Not enough data
                return
            
            # Scale and encode
            if 'behavior_scaler' not in self.scalers:
                self.scalers['behavior_scaler'] = StandardScaler()
                X_scaled = self.scalers['behavior_scaler'].fit_transform(X)
            else:
                X_scaled = self.scalers['behavior_scaler'].transform(X)
            
            if 'behavior_encoder' not in self.scalers:
                self.scalers['behavior_encoder'] = LabelEncoder()
                y_encoded = self.scalers['behavior_encoder'].fit_transform(y)
            else:
                y_encoded = self.scalers['behavior_encoder'].transform(y)
            
            # Train Random Forest
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_encoded, test_size=0.2, random_state=42
            )
            
            self.models['random_forest'] = RandomForestClassifier(
                n_estimators=100,
                random_state=42,
                n_jobs=-1
            )
            self.models['random_forest'].fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.models['random_forest'].predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.logger.info(f"Behavior classifier trained with accuracy: {accuracy:.3f}")
            
        except Exception as e:
            self.logger.error(f"Error training behavior classifier: {e}")
    
    def train_neural_network(self, training_data: pd.DataFrame):
        """Train neural network model using PyTorch"""
        if not TORCH_AVAILABLE:
            return
        
        try:
            # Prepare data
            feature_columns = [
                'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                'login_frequency', 'zone_changes', 'avg_session_length'
            ]
            
            X = training_data[feature_columns].fillna(0).values
            y = training_data['risk_score'].fillna(0).values
            
            if len(X) < 50:  # Need more data for neural network
                return
            
            # Convert to tensors
            X_tensor = torch.FloatTensor(X).to(self.device)
            y_tensor = torch.FloatTensor(y).to(self.device)
            
            # Simple neural network
            class BehaviorNet(nn.Module):
                def __init__(self, input_size):
                    super(BehaviorNet, self).__init__()
                    self.layers = nn.Sequential(
                        nn.Linear(input_size, 64),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(64, 32),
                        nn.ReLU(),
                        nn.Dropout(0.2),
                        nn.Linear(32, 16),
                        nn.ReLU(),
                        nn.Linear(16, 1),
                        nn.Sigmoid()
                    )
                
                def forward(self, x):
                    return self.layers(x)
            
            # Initialize and train model
            model = BehaviorNet(X.shape[1]).to(self.device)
            criterion = nn.MSELoss()
            optimizer = optim.Adam(model.parameters(), lr=self.config['learning_rate'])
            
            # Training loop
            model.train()
            for epoch in range(self.config['epochs']):
                optimizer.zero_grad()
                outputs = model(X_tensor)
                loss = criterion(outputs.squeeze(), y_tensor)
                loss.backward()
                optimizer.step()
                
                if epoch % 20 == 0:
                    self.logger.debug(f"Epoch {epoch}, Loss: {loss.item():.4f}")
            
            self.models['neural_network'] = model
            self.logger.info("Neural network trained successfully")
            
        except Exception as e:
            self.logger.error(f"Error training neural network: {e}")
    
    def predict_player_behavior(self, player_data: Dict) -> Dict[str, Any]:
        """Predict player behavior using trained models"""
        try:
            # Convert to DataFrame for preprocessing
            df = pd.DataFrame([player_data])
            df = self.preprocess_player_data([player_data])
            
            if df.empty:
                return {"error": "Invalid data"}
            
            predictions = {}
            
            # Anomaly detection
            if 'isolation_forest' in self.models and 'anomaly_scaler' in self.scalers:
                feature_columns = [
                    'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                    'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                    'login_frequency', 'zone_changes', 'avg_session_length', 'risk_score'
                ]
                X = df[feature_columns].fillna(0)
                X_scaled = self.scalers['anomaly_scaler'].transform(X)
                anomaly_score = self.models['isolation_forest'].decision_function(X_scaled)[0]
                predictions['anomaly_score'] = float(anomaly_score)
                predictions['is_anomaly'] = anomaly_score < 0
            
            # Behavior classification
            if 'random_forest' in self.models and 'behavior_scaler' in self.scalers:
                feature_columns = [
                    'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                    'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                    'login_frequency', 'zone_changes', 'avg_session_length'
                ]
                X = df[feature_columns].fillna(0)
                X_scaled = self.scalers['behavior_scaler'].transform(X)
                behavior_pred = self.models['random_forest'].predict(X_scaled)[0]
                behavior_proba = self.models['random_forest'].predict_proba(X_scaled)[0]
                
                predictions['behavior_class'] = self.scalers['behavior_encoder'].inverse_transform([behavior_pred])[0]
                predictions['behavior_confidence'] = float(max(behavior_proba))
            
            # Neural network prediction
            if 'neural_network' in self.models and TORCH_AVAILABLE:
                feature_columns = [
                    'hour', 'day_of_week', 'position_distance', 'hp_percentage',
                    'mp_percentage', 'actions_per_minute', 'chat_messages_per_hour',
                    'login_frequency', 'zone_changes', 'avg_session_length'
                ]
                X = df[feature_columns].fillna(0).values
                X_tensor = torch.FloatTensor(X).to(self.device)
                
                self.models['neural_network'].eval()
                with torch.no_grad():
                    nn_pred = self.models['neural_network'](X_tensor).cpu().numpy()[0, 0]
                predictions['neural_risk_score'] = float(nn_pred)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting behavior: {e}")
            return {"error": str(e)}
    
    def learn_from_interaction(self, player_data: Dict, outcome: str):
        """Learn from GM-player interactions"""
        if not self.learning_enabled:
            return
        
        try:
            # Add interaction data to cache
            interaction_data = {
                **player_data,
                'outcome': outcome,
                'timestamp': datetime.now(),
                'feedback_type': 'gm_interaction'
            }
            
            self.data_cache.append(interaction_data)
            
            # Retrain if cache is full
            if len(self.data_cache) >= self.config['model_save_interval']:
                self._retrain_models()
                self.data_cache = []  # Clear cache
                
        except Exception as e:
            self.logger.error(f"Error learning from interaction: {e}")
    
    def start_learning_session(self, session_data: Dict):
        """Start a new GM learning session"""
        try:
            self.gm_learning_session = {
                'session_id': f"gm_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'start_time': datetime.now(),
                'session_data': session_data,
                'actions_learned': 0,
                'patterns_identified': []
            }
            
            self.logger.info(f"Started GM learning session: {self.gm_learning_session['session_id']}")
            
        except Exception as e:
            self.logger.error(f"Error starting GM learning session: {e}")
    
    def learn_from_gm_interaction(self, action_data: Dict, context_data: Dict, learning_data: Dict):
        """Learn from a specific GM action"""
        try:
            if not hasattr(self, 'gm_learning_session'):
                return
            
            # Process the GM action for learning
            learning_example = {
                'gm_name': action_data.get('gm_name'),
                'action_type': learning_data.get('action_type'),
                'severity_handling': learning_data.get('severity_handling'),
                'context': context_data,
                'timestamp': action_data.get('timestamp'),
                'escalation_pattern': learning_data.get('escalation_pattern'),
                'server_state': context_data.get('server_load', {}),
                'outcome_type': 'human_gm_decision'
            }
            
            # Add to learning cache
            self.data_cache.append(learning_example)
            self.gm_learning_session['actions_learned'] += 1
            
            # Identify patterns
            pattern = self._identify_gm_action_pattern(learning_example)
            if pattern:
                self.gm_learning_session['patterns_identified'].append(pattern)
            
            # Update models incrementally if possible
            if self.gm_learning_session['actions_learned'] % 10 == 0:
                self._update_models_incrementally()
            
            self.logger.debug(f"Learned from GM action: {action_data.get('command')} (session: {self.gm_learning_session['actions_learned']} actions)")
            
        except Exception as e:
            self.logger.error(f"Error learning from GM interaction: {e}")
    
    def predict_action(self, incident, warning_count: int, autonomous_mode: bool = True):
        """Predict the best action based on learned patterns from GMs"""
        try:
            if not self.models:
                return None
            
            # Create feature vector for action prediction
            features = {
                'severity': self._severity_to_numeric(incident.severity),
                'warning_count': warning_count,
                'incident_type': self._incident_type_to_numeric(incident.incident_type),
                'autonomous_mode': 1 if autonomous_mode else 0,
                'time_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday()
            }
            
            # Use learned patterns to predict action
            if hasattr(self, 'gm_learning_session') and self.gm_learning_session.get('patterns_identified'):
                action = self._predict_action_from_patterns(features, incident)
                if action:
                    return action
            
            # Fallback to default ML prediction
            return self._predict_action_ml(features, autonomous_mode)
            
        except Exception as e:
            self.logger.error(f"Error predicting action: {e}")
            return None
    
    def _identify_gm_action_pattern(self, learning_example: Dict) -> Optional[Dict]:
        """Identify patterns from GM actions"""
        try:
            pattern = {
                'action_type': learning_example.get('action_type'),
                'severity': learning_example.get('severity_handling'),
                'context_server_load': learning_example.get('context', {}).get('server_load', {}),
                'escalation_immediate': learning_example.get('escalation_pattern', {}).get('immediate_action', False),
                'time_pattern': {
                    'hour': learning_example.get('timestamp', datetime.now()).hour,
                    'day_of_week': learning_example.get('timestamp', datetime.now()).weekday()
                }
            }
            
            return pattern
            
        except Exception as e:
            self.logger.error(f"Error identifying GM action pattern: {e}")
            return None
    
    def _predict_action_from_patterns(self, features: Dict, incident) -> Optional[str]:
        """Predict action based on learned GM patterns"""
        try:
            if not hasattr(self, 'gm_learning_session'):
                return None
            
            patterns = self.gm_learning_session.get('patterns_identified', [])
            if not patterns:
                return None
            
            # Find matching patterns
            matching_patterns = []
            for pattern in patterns:
                if (pattern.get('severity') == features.get('severity') or 
                    pattern.get('action_type') == self._incident_type_to_action_type(incident.incident_type)):
                    matching_patterns.append(pattern)
            
            if matching_patterns:
                # Return the most common action from matching patterns
                most_common_pattern = max(matching_patterns, key=lambda p: patterns.count(p))
                return self._pattern_to_action(most_common_pattern, features.get('autonomous_mode', 1))
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error predicting action from patterns: {e}")
            return None
    
    def _predict_action_ml(self, features: Dict, autonomous_mode: bool):
        """Use ML models to predict action"""
        # This is a simplified implementation - in practice you'd use trained models
        severity = features.get('severity', 0)
        warning_count = features.get('warning_count', 0)
        
        from ai_gm_service import AIGMAction  # Import here to avoid circular import
        
        if autonomous_mode:
            # More aggressive in autonomous mode
            if severity >= 4:
                return AIGMAction.JAIL
            elif severity >= 3:
                return AIGMAction.TEMP_JAIL
            elif warning_count >= 1:
                return AIGMAction.TEMP_JAIL
            else:
                return AIGMAction.WARN
        else:
            # Conservative in learning mode
            if severity >= 4:
                return AIGMAction.ESCALATE_GM3
            elif severity >= 3:
                return AIGMAction.ESCALATE_GM2
            else:
                return AIGMAction.WARN
    
    def _severity_to_numeric(self, severity) -> int:
        """Convert severity to numeric value"""
        severity_map = {
            'info': 1,
            'warning': 2,
            'moderate': 3,
            'severe': 4,
            'critical': 5
        }
        return severity_map.get(str(severity).lower(), 1)
    
    def _incident_type_to_numeric(self, incident_type: str) -> int:
        """Convert incident type to numeric value"""
        incident_map = {
            'stuck_player': 1,
            'suspicious_login': 2,
            'long_jail_time': 3,
            'extended_death': 4,
            'ml_anomaly_detected': 5,
            'ml_behavior_classification': 6
        }
        return incident_map.get(incident_type, 0)
    
    def _incident_type_to_action_type(self, incident_type: str) -> str:
        """Map incident type to action type"""
        mapping = {
            'stuck_player': 'assistance',
            'suspicious_login': 'disciplinary',
            'long_jail_time': 'administrative',
            'extended_death': 'assistance',
            'ml_anomaly_detected': 'disciplinary',
            'ml_behavior_classification': 'disciplinary'
        }
        return mapping.get(incident_type, 'other')
    
    def _pattern_to_action(self, pattern: Dict, autonomous_mode: int):
        """Convert a learned pattern to an action"""
        from ai_gm_service import AIGMAction  # Import here to avoid circular import
        
        action_type = pattern.get('action_type', 'other')
        escalation_immediate = pattern.get('escalation_immediate', False)
        
        if action_type == 'disciplinary':
            if escalation_immediate:
                return AIGMAction.TEMP_JAIL if autonomous_mode else AIGMAction.ESCALATE_GM2
            else:
                return AIGMAction.WARN
        elif action_type == 'assistance':
            return AIGMAction.WARN
        elif action_type == 'administrative':
            return AIGMAction.ESCALATE_GM2 if not autonomous_mode else AIGMAction.TEMP_JAIL
        else:
            return AIGMAction.WARN
    
    def _update_models_incrementally(self):
        """Update models incrementally with new data"""
        try:
            if len(self.data_cache) < 5:  # Need minimum data for updates
                return
            
            self.logger.debug(f"Incrementally updating models with {len(self.data_cache)} new examples")
            
            # This is a simplified implementation - in practice you'd do incremental learning
            # For now, we just validate the new data and prepare it for next full retraining
            
        except Exception as e:
            self.logger.error(f"Error in incremental model update: {e}")
    
    def _retrain_models(self):
        """Retrain models with new data"""
        try:
            if not self.data_cache:
                return
            
            # Convert cache to DataFrame
            df = pd.DataFrame(self.data_cache)
            df = self.preprocess_player_data(self.data_cache)
            
            if len(df) < 10:
                return
            
            self.logger.info(f"Retraining models with {len(df)} new samples")
            
            # Retrain all models
            self.train_anomaly_detector(df)
            self.train_behavior_classifier(df)
            if TORCH_AVAILABLE:
                self.train_neural_network(df)
            
            # Save models
            self.save_models()
            
        except Exception as e:
            self.logger.error(f"Error retraining models: {e}")
    
    def save_models(self, save_path: str = "AI-GM/models"):
        """Save trained models"""
        try:
            os.makedirs(save_path, exist_ok=True)
            
            # Save scikit-learn models
            for name, model in self.models.items():
                if name in ['isolation_forest', 'random_forest']:
                    with open(f"{save_path}/{name}.pkl", 'wb') as f:
                        pickle.dump(model, f)
            
            # Save scalers
            for name, scaler in self.scalers.items():
                with open(f"{save_path}/{name}.pkl", 'wb') as f:
                    pickle.dump(scaler, f)
            
            # Save PyTorch models
            if 'neural_network' in self.models and TORCH_AVAILABLE:
                torch.save(self.models['neural_network'].state_dict(), 
                          f"{save_path}/neural_network.pth")
            
            self.logger.info(f"Models saved to {save_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving models: {e}")
    
    def load_models(self, load_path: str = "AI-GM/models"):
        """Load trained models"""
        try:
            if not os.path.exists(load_path):
                self.logger.info("No saved models found, starting fresh")
                return
            
            # Load scikit-learn models
            for model_name in ['isolation_forest', 'random_forest']:
                model_path = f"{load_path}/{model_name}.pkl"
                if os.path.exists(model_path):
                    with open(model_path, 'rb') as f:
                        self.models[model_name] = pickle.load(f)
            
            # Load scalers
            for scaler_name in ['anomaly_scaler', 'behavior_scaler', 'behavior_encoder']:
                scaler_path = f"{load_path}/{scaler_name}.pkl"
                if os.path.exists(scaler_path):
                    with open(scaler_path, 'rb') as f:
                        self.scalers[scaler_name] = pickle.load(f)
            
            # Load PyTorch models
            if TORCH_AVAILABLE:
                nn_path = f"{load_path}/neural_network.pth"
                if os.path.exists(nn_path):
                    # Recreate model architecture
                    from torch import nn
                    class BehaviorNet(nn.Module):
                        def __init__(self, input_size):
                            super(BehaviorNet, self).__init__()
                            self.layers = nn.Sequential(
                                nn.Linear(input_size, 64),
                                nn.ReLU(),
                                nn.Dropout(0.2),
                                nn.Linear(64, 32),
                                nn.ReLU(),
                                nn.Dropout(0.2),
                                nn.Linear(32, 16),
                                nn.ReLU(),
                                nn.Linear(16, 1),
                                nn.Sigmoid()
                            )
                        
                        def forward(self, x):
                            return self.layers(x)
                    
                    model = BehaviorNet(10).to(self.device)
                    model.load_state_dict(torch.load(nn_path, map_location=self.device))
                    self.models['neural_network'] = model
            
            self.logger.info(f"Models loaded from {load_path}")
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
    
    def get_hardware_status(self) -> Dict[str, Any]:
        """Get current hardware utilization status"""
        status = {
            "platform": self.hardware_info.platform,
            "backend": self.hardware_info.recommended_backend,
            "device": str(self.device),
            "models_loaded": list(self.models.keys()),
            "cache_size": len(self.data_cache)
        }
        
        # GPU utilization (NVIDIA)
        if self.hardware_info.has_cuda and TORCH_AVAILABLE:
            try:
                status["gpu_memory_allocated"] = torch.cuda.memory_allocated()
                status["gpu_memory_reserved"] = torch.cuda.memory_reserved()
                status["gpu_utilization"] = f"{torch.cuda.utilization()}%"
            except:
                pass
        
        # CPU utilization
        try:
            import psutil
            status["cpu_usage"] = f"{psutil.cpu_percent()}%"
            status["memory_usage"] = f"{psutil.virtual_memory().percent}%"
        except ImportError:
            pass
        
        return status

# Example usage and testing
if __name__ == "__main__":
    # Initialize ML engine
    ml_engine = AIGMMLEngine()
    
    # Example player data for testing
    test_data = [{
        'player_id': 1,
        'timestamp': datetime.now(),
        'zone_id': 230,
        'pos_x': 100.0,
        'pos_y': 0.0,
        'pos_z': 150.0,
        'hp_percentage': 0.8,
        'mp_percentage': 0.6,
        'actions_per_minute': 5.2,
        'chat_messages_per_hour': 12,
        'login_duration_minutes': 120.0,
        'death_count': 2,
        'jail_history': 0,
        'gm_interactions': 1
    }]
    
    # Preprocess and train
    df = ml_engine.preprocess_player_data(test_data)
    ml_engine.train_anomaly_detector(df)
    ml_engine.train_behavior_classifier(df)
    ml_engine.train_neural_network(df)
    
    # Make prediction
    prediction = ml_engine.predict_player_behavior(test_data[0])
    print("Prediction result:", prediction)
    
    # Show hardware status
    status = ml_engine.get_hardware_status()
    print("Hardware status:", status)