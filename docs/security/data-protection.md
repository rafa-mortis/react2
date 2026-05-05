# Data Protection

This document describes data protection measures for the React Login Application.

## 🎯 Purpose

Data protection ensures:
- Compliance with data protection regulations
- Secure data handling and storage
- User privacy protection
- Proper data lifecycle management

## 🛡️ Data Classification

### 1. Data Categories

#### Personal Data
- **Email addresses**: User identification and communication
- **IP addresses**: Network location and security
- **User roles**: Access control and permissions
- **Authentication tokens**: Session management

#### Sensitive Data
- **Password hashes**: User authentication
- **Session identifiers**: User sessions
- **Security logs**: Security events and violations
- **Error logs**: Application errors and exceptions

#### System Data
- **Application logs**: System operation logs
- **Performance metrics**: Application performance data
- **Database metadata**: Database structure and statistics
- **Configuration data**: Application configuration

### 2. Data Sensitivity Levels

#### Level 1: Public
- Application UI content
- Public documentation
- Marketing materials

#### Level 2: Internal
- System configuration
- Performance metrics
- Internal documentation

#### Level 3: Confidential
- User personal data
- Authentication information
- Security logs

#### Level 4: Restricted
- Database credentials
- API keys and secrets
- Encryption keys

## 🔐 Encryption and Hashing

### 1. Password Security

#### Password Hashing Implementation
```python
# backend/security/password_security.py
import hashlib
import secrets
import bcrypt
from typing import Tuple

class PasswordSecurity:
    @staticmethod
    def hash_password_bcrypt(password: str) -> str:
        """Hash password using bcrypt (recommended)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password_bcrypt(password: str, hashed: str) -> bool:
        """Verify password using bcrypt"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def hash_password_sha256(password: str) -> str:
        """Hash password using SHA-256 with salt (current implementation)"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${password_hash}"
    
    @staticmethod
    def verify_password_sha256(password: str, stored_hash: str) -> bool:
        """Verify password using SHA-256"""
        try:
            salt, hash_value = stored_hash.split('$')
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == hash_value
        except ValueError:
            return False
    
    @staticmethod
    def migrate_password_hash(password: str, old_hash: str) -> str:
        """Migrate from SHA-256 to bcrypt"""
        if PasswordSecurity.verify_password_sha256(password, old_hash):
            return PasswordSecurity.hash_password_bcrypt(password)
        return None
```

### 2. Data Encryption

#### Sensitive Data Encryption
```python
# backend/security/encryption.py
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class DataEncryption:
    def __init__(self, password: str):
        self.password = password.encode()
        self.salt = os.environ.get('ENCRYPTION_SALT', 'default_salt').encode()
        self.key = self._derive_key()
        self.cipher = Fernet(self.key)
    
    def _derive_key(self) -> bytes:
        """Derive encryption key from password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password))
        return key
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    @staticmethod
    def generate_key() -> str:
        """Generate new encryption key"""
        return Fernet.generate_key().decode()
```

### 3. Database Encryption

#### Database Field Encryption
```python
# backend/models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from security.encryption import DataEncryption

Base = declarative_base()

class EncryptedUser(Base):
    __tablename__ = 'encrypted_users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    encrypted_phone = Column(Text)  # Encrypted phone number
    encrypted_address = Column(Text)  # Encrypted address
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default='normal')
    
    def __init__(self, email: str, password: str, phone: str = None, address: str = None):
        self.email = email
        self.password_hash = PasswordSecurity.hash_password_bcrypt(password)
        
        # Encrypt sensitive fields
        if phone:
            encryption = DataEncryption(os.environ.get('ENCRYPTION_KEY'))
            self.encrypted_phone = encryption.encrypt_data(phone)
        
        if address:
            encryption = DataEncryption(os.environ.get('ENCRYPTION_KEY'))
            self.encrypted_address = encryption.encrypt_data(address)
    
    def get_phone(self) -> str:
        """Decrypt phone number"""
        if self.encrypted_phone:
            encryption = DataEncryption(os.environ.get('ENCRYPTION_KEY'))
            return encryption.decrypt_data(self.encrypted_phone)
        return None
    
    def get_address(self) -> str:
        """Decrypt address"""
        if self.encrypted_address:
            encryption = DataEncryption(os.environ.get('ENCRYPTION_KEY'))
            return encryption.decrypt_data(self.encrypted_address)
        return None
```

## 📊 Data Access Control

### 1. Role-Based Access Control

#### Permission Management
```python
# backend/security/permissions.py
from enum import Enum
from typing import List, Dict, Set

class Permission(Enum):
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    DELETE_USERS = "delete_users"
    READ_LOGS = "read_logs"
    WRITE_LOGS = "write_logs"
    ADMIN_ACCESS = "admin_access"

class Role(Enum):
    GUEST = "guest"
    NORMAL = "normal"
    ADMIN = "admin"

# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.GUEST: set(),
    Role.NORMAL: {Permission.READ_USERS},
    Role.ADMIN: {
        Permission.READ_USERS,
        Permission.WRITE_USERS,
        Permission.DELETE_USERS,
        Permission.READ_LOGS,
        Permission.WRITE_LOGS,
        Permission.ADMIN_ACCESS
    }
}

class PermissionManager:
    @staticmethod
    def has_permission(user_role: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        try:
            role = Role(user_role)
            return permission in ROLE_PERMISSIONS.get(role, set())
        except ValueError:
            return False
    
    @staticmethod
    def get_user_permissions(user_role: str) -> List[Permission]:
        """Get all permissions for a user role"""
        try:
            role = Role(user_role)
            return list(ROLE_PERMISSIONS.get(role, set()))
        except ValueError:
            return []
    
    @staticmethod
    def require_permission(permission: Permission):
        """Decorator to require specific permission"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get user from session or token
                user_role = get_current_user_role()
                
                if not PermissionManager.has_permission(user_role, permission):
                    return jsonify({
                        'success': False,
                        'message': 'Insufficient permissions'
                    }), 403
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
```

### 2. Data Access Logging

#### Audit Logging
```python
# backend/security/audit_logging.py
import logging
from datetime import datetime
from typing import Dict, Any, Optional

audit_logger = logging.getLogger('audit')

class AuditLogger:
    @staticmethod
    def log_data_access(user_id: str, resource: str, action: str, 
                      ip_address: str, success: bool, details: Dict[str, Any] = None):
        """Log data access events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_access',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'ip_address': ip_address,
            'success': success,
            'details': details or {}
        }
        audit_logger.info(f"DATA_ACCESS: {event}")
    
    @staticmethod
    def log_data_modification(user_id: str, resource: str, action: str,
                           old_values: Dict[str, Any], new_values: Dict[str, Any],
                           ip_address: str):
        """Log data modification events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_modification',
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'ip_address': ip_address,
            'old_values': old_values,
            'new_values': new_values
        }
        audit_logger.info(f"DATA_MODIFICATION: {event}")
    
    @staticmethod
    def log_data_deletion(user_id: str, resource: str, resource_id: str,
                        ip_address: str, reason: str = None):
        """Log data deletion events"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'data_deletion',
            'user_id': user_id,
            'resource': resource,
            'resource_id': resource_id,
            'ip_address': ip_address,
            'reason': reason
        }
        audit_logger.warning(f"DATA_DELETION: {event}")
    
    @staticmethod
    def log_sensitive_data_access(user_id: str, data_type: str, record_id: str,
                               ip_address: str, purpose: str):
        """Log access to sensitive data"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'sensitive_data_access',
            'user_id': user_id,
            'data_type': data_type,
            'record_id': record_id,
            'ip_address': ip_address,
            'purpose': purpose
        }
        audit_logger.warning(f"SENSITIVE_DATA_ACCESS: {event}")
```

## 🗂️ Data Lifecycle Management

### 1. Data Retention

#### Retention Policy
```python
# backend/policies/retention_policy.py
from datetime import datetime, timedelta
from typing import Dict, Any

RETENTION_POLICY = {
    'user_data': {
        'retention_period': timedelta(days=365 * 7),  # 7 years
        'anonymize_after': timedelta(days=365 * 2),   # 2 years
        'delete_after': timedelta(days=365 * 7)        # 7 years
    },
    'security_logs': {
        'retention_period': timedelta(days=365),        # 1 year
        'anonymize_after': timedelta(days=90),          # 90 days
        'delete_after': timedelta(days=365)             # 1 year
    },
    'application_logs': {
        'retention_period': timedelta(days=90),         # 90 days
        'anonymize_after': timedelta(days=30),         # 30 days
        'delete_after': timedelta(days=90)              # 90 days
    },
    'session_data': {
        'retention_period': timedelta(hours=24),        # 24 hours
        'anonymize_after': timedelta(hours=1),          # 1 hour
        'delete_after': timedelta(hours=24)             # 24 hours
    }
}

class DataRetentionManager:
    @staticmethod
    def should_anonymize(data_type: str, created_at: datetime) -> bool:
        """Check if data should be anonymized"""
        policy = RETENTION_POLICY.get(data_type)
        if not policy:
            return False
        
        return datetime.now() - created_at > policy['anonymize_after']
    
    @staticmethod
    def should_delete(data_type: str, created_at: datetime) -> bool:
        """Check if data should be deleted"""
        policy = RETENTION_POLICY.get(data_type)
        if not policy:
            return False
        
        return datetime.now() - created_at > policy['delete_after']
    
    @staticmethod
    def anonymize_user_data(user_id: str) -> bool:
        """Anonymize user data"""
        try:
            db = next(get_db())
            
            # Anonymize personal data
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if user:
                user.email = f"anonymized_{user_id}@example.com"
                user.phone = None
                user.address = None
                db.commit()
                
                AuditLogger.log_data_modification(
                    'system', 'user', 'anonymize',
                    {'email': user.email},
                    {'email': f"anonymized_{user_id}@example.com"},
                    'system'
                )
            
            return True
        except Exception as e:
            audit_logger.error(f"Failed to anonymize user data: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def delete_expired_data():
        """Delete expired data based on retention policy"""
        try:
            db = next(get_db())
            
            # Delete expired session data
            expired_sessions = db.execute(
                "SELECT id FROM sessions WHERE created_at < :cutoff",
                {'cutoff': datetime.now() - RETENTION_POLICY['session_data']['delete_after']}
            ).fetchall()
            
            for session in expired_sessions:
                db.execute("DELETE FROM sessions WHERE id = :id", {'id': session.id})
            
            # Delete old application logs
            # Implementation depends on your logging system
            
            db.commit()
            audit_logger.info(f"Deleted {len(expired_sessions)} expired sessions")
            
        except Exception as e:
            audit_logger.error(f"Failed to delete expired data: {str(e)}")
        finally:
            db.close()
```

### 2. Data Backup and Recovery

#### Backup Procedures
```python
# backend/backup/data_backup.py
import subprocess
import os
import gzip
from datetime import datetime
from typing import Dict, List

class DataBackup:
    def __init__(self, backup_dir: str = '/backups'):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_database_backup(self) -> str:
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"database_backup_{timestamp}.sql")
        
        try:
            # Create database dump
            cmd = [
                'pg_dump',
                '-h', 'db',
                '-U', 'postgres',
                '-d', 'appdb',
                '-f', backup_file
            ]
            subprocess.run(cmd, check=True)
            
            # Compress backup
            compressed_file = f"{backup_file}.gz"
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Remove uncompressed backup
            os.remove(backup_file)
            
            audit_logger.info(f"Database backup created: {compressed_file}")
            return compressed_file
            
        except Exception as e:
            audit_logger.error(f"Database backup failed: {str(e)}")
            raise
    
    def create_user_data_backup(self) -> str:
        """Create user data backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"user_data_backup_{timestamp}.json")
        
        try:
            db = next(get_db())
            
            # Export user data
            users = db.execute("SELECT * FROM users").fetchall()
            
            # Convert to JSON
            import json
            user_data = []
            for user in users:
                user_dict = {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                user_data.append(user_dict)
            
            with open(backup_file, 'w') as f:
                json.dump(user_data, f, indent=2)
            
            audit_logger.info(f"User data backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            audit_logger.error(f"User data backup failed: {str(e)}")
            raise
        finally:
            db.close()
    
    def restore_database_backup(self, backup_file: str) -> bool:
        """Restore database from backup"""
        try:
            # Decompress if needed
            if backup_file.endswith('.gz'):
                decompressed_file = backup_file[:-3]
                with gzip.open(backup_file, 'rt') as f_in:
                    with open(decompressed_file, 'w') as f_out:
                        f_out.write(f_in.read())
                backup_file = decompressed_file
            
            # Restore database
            cmd = [
                'psql',
                '-h', 'db',
                '-U', 'postgres',
                '-d', 'appdb',
                '-f', backup_file
            ]
            subprocess.run(cmd, check=True)
            
            audit_logger.info(f"Database restored from: {backup_file}")
            return True
            
        except Exception as e:
            audit_logger.error(f"Database restore failed: {str(e)}")
            return False
```

## 🌐 GDPR Compliance

### 1. Data Subject Rights

#### Right to Access
```python
# backend/gdpr/data_subject_rights.py
from typing import Dict, Any, Optional

class DataSubjectRights:
    @staticmethod
    def get_user_data_export(user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR right to access"""
        try:
            db = next(get_db())
            
            # Get user data
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not user:
                return None
            
            # Collect all user-related data
            user_data = {
                'personal_data': {
                    'id': user.id,
                    'email': user.email,
                    'role': user.role,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                },
                'activity_logs': DataSubjectRights._get_user_activity_logs(user_id),
                'session_data': DataSubjectRights._get_user_sessions(user_id),
                'security_events': DataSubjectRights._get_user_security_events(user_id)
            }
            
            # Log data export
            AuditLogger.log_data_access(
                user_id, 'user_profile', 'data_export',
                request.remote_addr, True,
                {'purpose': 'GDPR right to access'}
            )
            
            return user_data
            
        except Exception as e:
            audit_logger.error(f"Failed to export user data: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def delete_user_data(user_id: str, reason: str = None) -> bool:
        """Delete user data for GDPR right to erasure"""
        try:
            db = next(get_db())
            
            # Get user data for audit
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            
            if user:
                # Delete user data
                db.execute("DELETE FROM users WHERE id = :user_id", {'user_id': user_id})
                db.execute("DELETE FROM sessions WHERE user_id = :user_id", {'user_id': user_id})
                
                db.commit()
                
                # Log deletion
                AuditLogger.log_data_deletion(
                    user_id, 'user_profile', user_id,
                    request.remote_addr, reason or 'GDPR right to erasure'
                )
                
                audit_logger.info(f"User data deleted for user_id: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            audit_logger.error(f"Failed to delete user data: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def anonymize_user_data(user_id: str) -> bool:
        """Anonymize user data for GDPR right to restriction"""
        try:
            db = next(get_db())
            
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if user:
                # Anonymize personal data
                user.email = f"anonymized_{user_id}@example.com"
                user.phone = None
                user.address = None
                
                db.commit()
                
                # Log anonymization
                AuditLogger.log_data_modification(
                    'system', 'user_profile', 'anonymize',
                    {'email': user.email},
                    {'email': f"anonymized_{user_id}@example.com"},
                    'system'
                )
                
                audit_logger.info(f"User data anonymized for user_id: {user_id}")
                return True
            
            return False
            
        except Exception as e:
            audit_logger.error(f"Failed to anonymize user data: {str(e)}")
            return False
        finally:
            db.close()
```

### 2. Consent Management

#### Consent Tracking
```python
# backend/gdpr/consent_management.py
from datetime import datetime
from typing import Dict, List, Optional

class ConsentManager:
    @staticmethod
    def record_consent(user_id: str, consent_type: str, granted: bool, 
                      ip_address: str, purpose: str = None) -> bool:
        """Record user consent"""
        try:
            db = next(get_db())
            
            # Insert consent record
            db.execute("""
                INSERT INTO consents (user_id, consent_type, granted, ip_address, purpose, created_at)
                VALUES (:user_id, :consent_type, :granted, :ip_address, :purpose, :created_at)
            """, {
                'user_id': user_id,
                'consent_type': consent_type,
                'granted': granted,
                'ip_address': ip_address,
                'purpose': purpose,
                'created_at': datetime.now()
            })
            
            db.commit()
            
            # Log consent
            AuditLogger.log_data_access(
                user_id, 'consent', 'record_consent',
                ip_address, True,
                {'consent_type': consent_type, 'granted': granted, 'purpose': purpose}
            )
            
            return True
            
        except Exception as e:
            audit_logger.error(f"Failed to record consent: {str(e)}")
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_user_consents(user_id: str) -> List[Dict]:
        """Get all user consents"""
        try:
            db = next(get_db())
            
            consents = db.execute("""
                SELECT consent_type, granted, purpose, created_at
                FROM consents
                WHERE user_id = :user_id
                ORDER BY created_at DESC
            """, {'user_id': user_id}).fetchall()
            
            return [
                {
                    'consent_type': consent.consent_type,
                    'granted': consent.granted,
                    'purpose': consent.purpose,
                    'created_at': consent.created_at.isoformat()
                }
                for consent in consents
            ]
            
        except Exception as e:
            audit_logger.error(f"Failed to get user consents: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def withdraw_consent(user_id: str, consent_type: str, ip_address: str) -> bool:
        """Withdraw user consent"""
        try:
            db = next(get_db())
            
            # Update consent record
            db.execute("""
                UPDATE consents 
                SET granted = false, withdrawn_at = :withdrawn_at
                WHERE user_id = :user_id AND consent_type = :consent_type
            """, {
                'user_id': user_id,
                'consent_type': consent_type,
                'withdrawn_at': datetime.now()
            })
            
            db.commit()
            
            # Log consent withdrawal
            AuditLogger.log_data_access(
                user_id, 'consent', 'withdraw_consent',
                ip_address, True,
                {'consent_type': consent_type}
            )
            
            return True
            
        except Exception as e:
            audit_logger.error(f"Failed to withdraw consent: {str(e)}")
            return False
        finally:
            db.close()
```

## 📊 Data Protection Impact Assessment

### 1. DPIA Template

#### Risk Assessment
```python
# backend/dpia/risk_assessment.py
from enum import Enum
from typing import Dict, List, Optional

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DataProtectionImpactAssessment:
    def __init__(self):
        self.assessment = {
            'project_name': '',
            'data_types': [],
            'processing_purposes': [],
            'risks': [],
            'mitigation_measures': [],
            'assessment_date': datetime.now().isoformat()
        }
    
    def add_data_type(self, data_type: str, sensitivity: RiskLevel, 
                     retention_period: str, legal_basis: str):
        """Add data type to assessment"""
        self.assessment['data_types'].append({
            'type': data_type,
            'sensitivity': sensitivity.value,
            'retention_period': retention_period,
            'legal_basis': legal_basis
        })
    
    def add_risk(self, risk_description: str, likelihood: RiskLevel, 
                 impact: RiskLevel, mitigation: str):
        """Add risk to assessment"""
        risk_level = self._calculate_risk_level(likelihood, impact)
        
        self.assessment['risks'].append({
            'description': risk_description,
            'likelihood': likelihood.value,
            'impact': impact.value,
            'risk_level': risk_level.value,
            'mitigation': mitigation
        })
    
    def _calculate_risk_level(self, likelihood: RiskLevel, impact: RiskLevel) -> RiskLevel:
        """Calculate overall risk level"""
        risk_matrix = {
            (RiskLevel.LOW, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.LOW, RiskLevel.MEDIUM): RiskLevel.LOW,
            (RiskLevel.LOW, RiskLevel.HIGH): RiskLevel.MEDIUM,
            (RiskLevel.LOW, RiskLevel.CRITICAL): RiskLevel.HIGH,
            (RiskLevel.MEDIUM, RiskLevel.LOW): RiskLevel.LOW,
            (RiskLevel.MEDIUM, RiskLevel.MEDIUM): RiskLevel.MEDIUM,
            (RiskLevel.MEDIUM, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.MEDIUM, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
            (RiskLevel.HIGH, RiskLevel.LOW): RiskLevel.MEDIUM,
            (RiskLevel.HIGH, RiskLevel.MEDIUM): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.HIGH): RiskLevel.HIGH,
            (RiskLevel.HIGH, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.LOW): RiskLevel.HIGH,
            (RiskLevel.CRITICAL, RiskLevel.MEDIUM): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.HIGH): RiskLevel.CRITICAL,
            (RiskLevel.CRITICAL, RiskLevel.CRITICAL): RiskLevel.CRITICAL,
        }
        
        return risk_matrix.get((likelihood, impact), RiskLevel.HIGH)
    
    def generate_report(self) -> Dict:
        """Generate DPIA report"""
        return {
            'assessment': self.assessment,
            'recommendations': self._generate_recommendations(),
            'approval_required': self._requires_approval()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []
        
        # Check for high-risk data types
        high_risk_data = [dt for dt in self.assessment['data_types'] 
                         if dt['sensitivity'] in ['high', 'critical']]
        
        if high_risk_data:
            recommendations.append("Implement additional security measures for high-risk data")
            recommendations.append("Consider data minimization for high-risk data types")
        
        # Check for high-risk processes
        high_risks = [risk for risk in self.assessment['risks'] 
                     if risk['risk_level'] in ['high', 'critical']]
        
        if high_risks:
            recommendations.append("Implement comprehensive risk mitigation measures")
            recommendations.append("Consider additional privacy safeguards")
        
        return recommendations
    
    def _requires_approval(self) -> bool:
        """Check if DPIA requires approval"""
        high_risks = [risk for risk in self.assessment['risks'] 
                     if risk['risk_level'] in ['high', 'critical']]
        
        return len(high_risks) > 0
```

## 📚 Best Practices

### 1. Data Protection

1. **Data Minimization**: Collect only necessary data
2. **Purpose Limitation**: Use data only for specified purposes
3. **Storage Limitation**: Store data only as long as necessary
4. **Security**: Implement appropriate technical and organizational measures
5. **Accountability**: Maintain records of processing activities

### 2. Privacy by Design

1. **Privacy Impact Assessment**: Conduct DPIA for new projects
2. **Default Settings**: Privacy-friendly default settings
3. **User Control**: Give users control over their data
4. **Transparency**: Be transparent about data processing
5. **Security**: Build security into the system from the start

### 3. Compliance

1. **Regulatory Compliance**: Follow applicable regulations
2. **Documentation**: Maintain comprehensive documentation
3. **Training**: Train staff on data protection
4. **Audits**: Conduct regular privacy audits
5. **Incident Response**: Have data breach response procedures

---

*For security scanning information, see [security-scanning.md](security-scanning.md).*
