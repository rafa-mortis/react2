# Security Scanning

This document describes security scanning procedures for the React Login Application.

## 🎯 Purpose

Security scanning ensures:
- Proactive vulnerability detection
- Compliance with security standards
- Continuous security monitoring
- Risk assessment and mitigation

## 🔍 Security Scanning Tools

### 1. Static Application Security Testing (SAST)

#### Bandit - Python Security Scanner
```python
# backend/.bandit
[bandit]
exclude_dirs = ['testes', 'migrations']
tests = ['B201', 'B301', 'B401', 'B501', 'B601', 'B701']
skips = ['B101', 'B601']

# backend/scripts/run_bandit.py
import subprocess
import json
import logging

def run_bandit_scan():
    """Run Bandit security scan"""
    try:
        # Run Bandit scan
        result = subprocess.run([
            'bandit',
            '-r', '.',
            '-f', 'json',
            '-o', 'bandit_report.json'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            logging.warning(f"Bandit scan completed with issues: {result.stderr}")
        
        # Parse results
        with open('bandit_report.json', 'r') as f:
            report = json.load(f)
        
        # Analyze results
        analyze_bandit_results(report)
        
        return report
        
    except Exception as e:
        logging.error(f"Bandit scan failed: {str(e)}")
        return None

def analyze_bandit_results(report):
    """Analyze Bandit scan results"""
    if not report.get('results'):
        print("✅ No security issues found by Bandit")
        return
    
    high_issues = [r for r in report['results'] if r['issue_severity'] == 'HIGH']
    medium_issues = [r for r in report['results'] if r['issue_severity'] == 'MEDIUM']
    low_issues = [r for r in report['results'] if r['issue_severity'] == 'LOW']
    
    print(f"🔍 Bandit Security Scan Results:")
    print(f"  High: {len(high_issues)}")
    print(f"  Medium: {len(medium_issues)}")
    print(f"  Low: {len(low_issues)}")
    
    # Print high severity issues
    if high_issues:
        print("\n🚨 High Severity Issues:")
        for issue in high_issues:
            print(f"  - {issue['test_name']}: {issue['issue_text']}")
            print(f"    File: {issue['filename']}:{issue['line_number']}")
    
    return len(high_issues) == 0 and len(medium_issues) == 0

if __name__ == "__main__":
    run_bandit_scan()
```

#### Semgrep - Multi-language Security Scanner
```yaml
# .semgrep.yml
rules:
  - id: sql-injection
    pattern: |
      execute($QUERY + $INPUT)
    message: Possible SQL injection vulnerability
    severity: ERROR
    languages: [python]
    
  - id: hardcoded-password
    pattern: |
      password = "..."
    message: Hardcoded password detected
    severity: ERROR
    languages: [python, javascript]
    
  - id: weak-crypto
    pattern: |
      hashlib.md5(...)
    message: Weak cryptographic algorithm detected
    severity: WARNING
    languages: [python]

# backend/scripts/run_semgrep.py
import subprocess
import json
import logging

def run_semgrep_scan():
    """Run Semgrep security scan"""
    try:
        # Run Semgrep scan
        result = subprocess.run([
            'semgrep',
            '--config=auto',
            '--json',
            '--output=semgrep_report.json',
            '.'
        ], capture_output=True, text=True)
        
        # Parse results
        with open('semgrep_report.json', 'r') as f:
            report = json.load(f)
        
        # Analyze results
        analyze_semgrep_results(report)
        
        return report
        
    except Exception as e:
        logging.error(f"Semgrep scan failed: {str(e)}")
        return None

def analyze_semgrep_results(report):
    """Analyze Semgrep scan results"""
    if not report.get('results'):
        print("✅ No security issues found by Semgrep")
        return True
    
    error_issues = [r for r in report['results'] if r['metadata']['severity'] == 'ERROR']
    warning_issues = [r for r in report['results'] if r['metadata']['severity'] == 'WARNING']
    info_issues = [r for r in report['results'] if r['metadata']['severity'] == 'INFO']
    
    print(f"🔍 Semgrep Security Scan Results:")
    print(f"  Error: {len(error_issues)}")
    print(f"  Warning: {len(warning_issues)}")
    print(f"  Info: {len(info_issues)}")
    
    # Print error issues
    if error_issues:
        print("\n🚨 Error Issues:")
        for issue in error_issues:
            print(f"  - {issue['metadata']['name']}: {issue['message']}")
            print(f"    File: {issue['path']}:{issue['start']['line']}")
    
    return len(error_issues) == 0

if __name__ == "__main__":
    run_semgrep_scan()
```

### 2. Dynamic Application Security Testing (DAST)

#### OWASP ZAP Integration
```python
# backend/scripts/run_zap_scan.py
import subprocess
import json
import time
import requests

class ZAPScanner:
    def __init__(self, target_url, api_key=None):
        self.target_url = target_url
        self.api_key = api_key
        self.zap_url = "http://localhost:8080"
    
    def start_zap_scan(self):
        """Start ZAP security scan"""
        try:
            # Start spider
            spider_id = self.start_spider()
            self.wait_for_spider(spider_id)
            
            # Start active scan
            scan_id = self.start_active_scan()
            self.wait_for_active_scan(scan_id)
            
            # Get results
            results = self.get_scan_results()
            
            return results
            
        except Exception as e:
            logging.error(f"ZAP scan failed: {str(e)}")
            return None
    
    def start_spider(self):
        """Start ZAP spider"""
        response = requests.get(f"{self.zap_url}/JSON/spider/action/scan/", params={
            'url': self.target_url,
            'apikey': self.api_key
        })
        
        return response.json()['scan']
    
    def wait_for_spider(self, spider_id):
        """Wait for spider to complete"""
        while True:
            response = requests.get(f"{self.zap_url}/JSON/spider/status/", params={
                'scanId': spider_id,
                'apikey': self.api_key
            })
            
            status = response.json()['status']
            if status == '100':
                break
            
            time.sleep(5)
    
    def start_active_scan(self):
        """Start ZAP active scan"""
        response = requests.get(f"{self.zap_url}/JSON/ascan/action/scan/", params={
            'url': self.target_url,
            'apikey': self.api_key
        })
        
        return response.json()['scan']
    
    def wait_for_active_scan(self, scan_id):
        """Wait for active scan to complete"""
        while True:
            response = requests.get(f"{self.zap_url}/JSON/ascan/status/", params={
                'scanId': scan_id,
                'apikey': self.api_key
            })
            
            status = response.json()['status']
            if status == '100':
                break
            
            time.sleep(10)
    
    def get_scan_results(self):
        """Get ZAP scan results"""
        response = requests.get(f"{self.zap_url}/JSON/core/view/alerts/", params={
            'apikey': self.api_key
        })
        
        return response.json()['alerts']

def run_zap_security_scan():
    """Run ZAP security scan"""
    scanner = ZAPScanner("http://localhost:5000")
    results = scanner.start_zap_scan()
    
    if results:
        analyze_zap_results(results)
    
    return results

def analyze_zap_results(results):
    """Analyze ZAP scan results"""
    if not results:
        print("✅ No security issues found by ZAP")
        return True
    
    high_issues = [r for r in results if r['risk'] == 'High']
    medium_issues = [r for r in results if r['risk'] == 'Medium']
    low_issues = [r for r in results if r['risk'] == 'Low']
    
    print(f"🔍 ZAP Security Scan Results:")
    print(f"  High: {len(high_issues)}")
    print(f"  Medium: {len(medium_issues)}")
    print(f"  Low: {len(low_issues)}")
    
    # Print high risk issues
    if high_issues:
        print("\n🚨 High Risk Issues:")
        for issue in high_issues:
            print(f"  - {issue['alert']}: {issue['desc']}")
            print(f"    URL: {issue['url']}")
    
    return len(high_issues) == 0

if __name__ == "__main__":
    run_zap_security_scan()
```

### 3. Dependency Security Scanning

#### Snyk Integration
```python
# backend/scripts/run_snyk_scan.py
import subprocess
import json
import logging

def run_snyk_scan():
    """Run Snyk security scan"""
    try:
        # Run Snyk scan
        result = subprocess.run([
            'snyk',
            'test',
            '--json',
            '--json-file-output=snyk_report.json'
        ], capture_output=True, text=True)
        
        # Parse results
        with open('snyk_report.json', 'r') as f:
            report = json.load(f)
        
        # Analyze results
        analyze_snyk_results(report)
        
        return report
        
    except Exception as e:
        logging.error(f"Snyk scan failed: {str(e)}")
        return None

def analyze_snyk_results(report):
    """Analyze Snyk scan results"""
    if not report.get('vulnerabilities'):
        print("✅ No vulnerabilities found by Snyk")
        return True
    
    critical_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'critical']
    high_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'high']
    medium_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'medium']
    low_vulns = [v for v in report['vulnerabilities'] if v['severity'] == 'low']
    
    print(f"🔍 Snyk Security Scan Results:")
    print(f"  Critical: {len(critical_vulns)}")
    print(f"  High: {len(high_vulns)}")
    print(f"  Medium: {len(medium_vulns)}")
    print(f"  Low: {len(low_vulns)}")
    
    # Print critical vulnerabilities
    if critical_vulns:
        print("\n🚨 Critical Vulnerabilities:")
        for vuln in critical_vulns:
            print(f"  - {vuln['title']}: {vuln['description']}")
            print(f"    Package: {vuln['packageName']}@{vuln['version']}")
    
    return len(critical_vulns) == 0 and len(high_vulns) == 0

if __name__ == "__main__":
    run_snyk_scan()
```

#### npm Audit for Frontend
```javascript
// frontend/scripts/run_npm_audit.js
const { execSync } = require('child_process');
const fs = require('fs');

function runNpmAudit() {
  try {
    // Run npm audit
    const auditOutput = execSync('npm audit --json', { encoding: 'utf8' });
    const auditReport = JSON.parse(auditOutput);
    
    // Analyze results
    analyzeNpmAuditResults(auditReport);
    
    return auditReport;
  } catch (error) {
    console.error('npm audit failed:', error.message);
    return null;
  }
}

function analyzeNpmAuditResults(report) {
  if (!report.vulnerabilities || Object.keys(report.vulnerabilities).length === 0) {
    console.log('✅ No vulnerabilities found by npm audit');
    return true;
  }
  
  const criticalVulns = Object.values(report.vulnerabilities).filter(v => v.severity === 'critical');
  const highVulns = Object.values(report.vulnerabilities).filter(v => v.severity === 'high');
  const mediumVulns = Object.values(report.vulnerabilities).filter(v => v.severity === 'medium');
  const lowVulns = Object.values(report.vulnerabilities).filter(v => v.severity === 'low');
  
  console.log('🔍 npm Audit Results:');
  console.log(`  Critical: ${criticalVulns.length}`);
  console.log(`  High: ${highVulns.length}`);
  console.log(`  Medium: ${mediumVulns.length}`);
  console.log(`  Low: ${lowVulns.length}`);
  
  // Print critical vulnerabilities
  if (criticalVulns.length > 0) {
    console.log('\n🚨 Critical Vulnerabilities:');
    criticalVulns.forEach(vuln => {
      console.log(`  - ${vuln.title}: ${vuln.url}`);
      console.log(`    Package: ${vuln.name}@${vuln.range}`);
    });
  }
  
  return criticalVulns.length === 0 && highVulns.length === 0;
}

if (require.main === module) {
  runNpmAudit();
}

module.exports = { runNpmAudit, analyzeNpmAuditResults };
```

## 📊 Security Scanning Pipeline

### 1. Automated Scanning Workflow

#### Security Scan Pipeline
```yaml
# .github/workflows/security-scan.yml
name: Security Scanning

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 2:00 AM UTC
    - cron: '0 2 * * *'

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
        
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
        
    - name: Install Python dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install bandit semgrep
        
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm ci
        
    - name: Run Bandit security scan
      run: |
        cd backend
        python scripts/run_bandit.py
        
    - name: Run Semgrep security scan
      run: |
        cd backend
        python scripts/run_semgrep.py
        
    - name: Run npm audit
      run: |
        cd frontend
        npm audit --audit-level=moderate
        
    - name: Run Snyk security scan
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
      run: |
        cd backend
        snyk test --json > snyk_report.json || true
        
    - name: Upload security reports
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          backend/bandit_report.json
          backend/semgrep_report.json
          backend/snyk_report.json
          frontend/npm-audit-report.json
```

### 2. Security Reporting

#### Security Report Generator
```python
# backend/scripts/generate_security_report.py
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class SecurityReportGenerator:
    def __init__(self):
        self.report = {
            'scan_date': datetime.now().isoformat(),
            'tools': {},
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'high_issues': 0,
                'medium_issues': 0,
                'low_issues': 0
            }
        }
    
    def add_bandit_results(self, file_path: str):
        """Add Bandit scan results"""
        try:
            with open(file_path, 'r') as f:
                bandit_report = json.load(f)
            
            self.report['tools']['bandit'] = {
                'total_issues': len(bandit_report.get('results', [])),
                'high_issues': len([r for r in bandit_report.get('results', []) if r['issue_severity'] == 'HIGH']),
                'medium_issues': len([r for r in bandit_report.get('results', []) if r['issue_severity'] == 'MEDIUM']),
                'low_issues': len([r for r in bandit_report.get('results', []) if r['issue_severity'] == 'LOW'])
            }
            
        except Exception as e:
            print(f"Error processing Bandit results: {str(e)}")
    
    def add_semgrep_results(self, file_path: str):
        """Add Semgrep scan results"""
        try:
            with open(file_path, 'r') as f:
                semgrep_report = json.load(f)
            
            self.report['tools']['semgrep'] = {
                'total_issues': len(semgrep_report.get('results', [])),
                'error_issues': len([r for r in semgrep_report.get('results', []) if r['metadata']['severity'] == 'ERROR']),
                'warning_issues': len([r for r in semgrep_report.get('results', []) if r['metadata']['severity'] == 'WARNING']),
                'info_issues': len([r for r in semgrep_report.get('results', []) if r['metadata']['severity'] == 'INFO'])
            }
            
        except Exception as e:
            print(f"Error processing Semgrep results: {str(e)}")
    
    def add_snyk_results(self, file_path: str):
        """Add Snyk scan results"""
        try:
            with open(file_path, 'r') as f:
                snyk_report = json.load(f)
            
            self.report['tools']['snyk'] = {
                'total_issues': len(snyk_report.get('vulnerabilities', [])),
                'critical_issues': len([v for v in snyk_report.get('vulnerabilities', []) if v['severity'] == 'critical']),
                'high_issues': len([v for v in snyk_report.get('vulnerabilities', []) if v['severity'] == 'high']),
                'medium_issues': len([v for v in snyk_report.get('vulnerabilities', []) if v['severity'] == 'medium']),
                'low_issues': len([v for v in snyk_report.get('vulnerabilities', []) if v['severity'] == 'low'])
            }
            
        except Exception as e:
            print(f"Error processing Snyk results: {str(e)}")
    
    def calculate_summary(self):
        """Calculate overall security summary"""
        for tool, results in self.report['tools'].items():
            self.report['summary']['total_issues'] += results.get('total_issues', 0)
            self.report['summary']['critical_issues'] += results.get('critical_issues', 0)
            self.report['summary']['high_issues'] += results.get('high_issues', 0)
            self.report['summary']['medium_issues'] += results.get('medium_issues', 0)
            self.report['summary']['low_issues'] += results.get('low_issues', 0)
    
    def generate_html_report(self) -> str:
        """Generate HTML security report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Scan Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; }}
                .tool-results {{ margin: 20px 0; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #388e3c; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Security Scan Report</h1>
                <p>Scan Date: {self.report['scan_date']}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr><th>Total Issues</th><td>{self.report['summary']['total_issues']}</td></tr>
                    <tr><th>Critical</th><td class="critical">{self.report['summary']['critical_issues']}</td></tr>
                    <tr><th>High</th><td class="high">{self.report['summary']['high_issues']}</td></tr>
                    <tr><th>Medium</th><td class="medium">{self.report['summary']['medium_issues']}</td></tr>
                    <tr><th>Low</th><td class="low">{self.report['summary']['low_issues']}</td></tr>
                </table>
            </div>
            
            <div class="tool-results">
                <h2>Tool Results</h2>
        """
        
        for tool, results in self.report['tools'].items():
            html += f"""
                <h3>{tool.title()}</h3>
                <table>
                    <tr><th>Total Issues</th><td>{results.get('total_issues', 0)}</td></tr>
                    <tr><th>Critical</th><td class="critical">{results.get('critical_issues', 0)}</td></tr>
                    <tr><th>High</th><td class="high">{results.get('high_issues', 0)}</td></tr>
                    <tr><th>Medium</th><td class="medium">{results.get('medium_issues', 0)}</td></tr>
                    <tr><th>Low</th><td class="low">{results.get('low_issues', 0)}</td></tr>
                </table>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, output_dir: str = 'security_reports'):
        """Save security report"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON report
        with open(f"{output_dir}/security_report.json", 'w') as f:
            json.dump(self.report, f, indent=2)
        
        # Save HTML report
        html_report = self.generate_html_report()
        with open(f"{output_dir}/security_report.html", 'w') as f:
            f.write(html_report)
        
        print(f"Security report saved to {output_dir}/")

def main():
    """Generate security report"""
    generator = SecurityReportGenerator()
    
    # Add scan results
    if os.path.exists('bandit_report.json'):
        generator.add_bandit_results('bandit_report.json')
    
    if os.path.exists('semgrep_report.json'):
        generator.add_semgrep_results('semgrep_report.json')
    
    if os.path.exists('snyk_report.json'):
        generator.add_snyk_results('snyk_report.json')
    
    # Calculate summary and generate report
    generator.calculate_summary()
    generator.save_report()

if __name__ == "__main__":
    main()
```

## 🚨 Security Incident Response

### 1. Security Incident Management

#### Incident Response Workflow
```python
# backend/security/incident_response.py
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

class SecurityIncidentManager:
    def __init__(self):
        self.incidents = []
        self.active_incidents = {}
    
    def create_incident(self, incident_type: str, severity: str, description: str, 
                       source: str, details: Dict[str, Any] = None) -> str:
        """Create new security incident"""
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{len(self.incidents) + 1:03d}"
        
        incident = {
            'id': incident_id,
            'type': incident_type,
            'severity': severity,
            'description': description,
            'source': source,
            'details': details or {},
            'status': 'open',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'actions': []
        }
        
        self.incidents.append(incident)
        self.active_incidents[incident_id] = incident
        
        # Log incident
        logging.warning(f"Security incident created: {incident_id} - {description}")
        
        return incident_id
    
    def update_incident(self, incident_id: str, status: str, action: str, 
                      details: Dict[str, Any] = None):
        """Update security incident"""
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        incident['status'] = status
        incident['updated_at'] = datetime.now().isoformat()
        
        incident['actions'].append({
            'action': action,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
        
        if status == 'resolved':
            del self.active_incidents[incident_id]
        
        logging.info(f"Security incident updated: {incident_id} - {action}")
        return True
    
    def get_active_incidents(self) -> List[Dict]:
        """Get active security incidents"""
        return list(self.active_incidents.values())
    
    def generate_incident_report(self, incident_id: str) -> Dict:
        """Generate incident report"""
        incident = None
        for inc in self.incidents:
            if inc['id'] == incident_id:
                incident = inc
                break
        
        if not incident:
            return None
        
        return {
            'incident': incident,
            'timeline': incident['actions'],
            'recommendations': self._generate_recommendations(incident)
        }
    
    def _generate_recommendations(self, incident: Dict) -> List[str]:
        """Generate incident recommendations"""
        recommendations = []
        
        if incident['type'] == 'sql_injection':
            recommendations.extend([
                "Review all database queries for proper parameterization",
                "Implement input validation and sanitization",
                "Add database access logging",
                "Conduct security code review"
            ])
        elif incident['type'] == 'xss':
            recommendations.extend([
                "Implement output encoding",
                "Add Content Security Policy headers",
                "Sanitize user input",
                "Review client-side validation"
            ])
        elif incident['type'] == 'authentication_bypass':
            recommendations.extend([
                "Review authentication logic",
                "Implement multi-factor authentication",
                "Add account lockout mechanisms",
                "Review session management"
            ])
        
        return recommendations

# Global incident manager instance
incident_manager = SecurityIncidentManager()
```

### 2. Security Alerting

#### Alert Configuration
```python
# backend/security/alerting.py
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any

class SecurityAlertManager:
    def __init__(self):
        self.email_config = {
            'smtp_server': os.environ.get('SMTP_SERVER'),
            'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
            'username': os.environ.get('SMTP_USERNAME'),
            'password': os.environ.get('SMTP_PASSWORD'),
            'from_email': os.environ.get('FROM_EMAIL'),
            'to_emails': os.environ.get('SECURITY_EMAILS', '').split(',')
        }
        
        self.slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    def send_security_alert(self, incident: Dict[str, Any]):
        """Send security alert"""
        if incident['severity'] in ['critical', 'high']:
            self.send_email_alert(incident)
            self.send_slack_alert(incident)
        
        # Log alert
        logging.critical(f"Security alert sent: {incident['id']} - {incident['description']}")
    
    def send_email_alert(self, incident: Dict[str, Any]):
        """Send email alert"""
        if not self.email_config['smtp_server']:
            return
        
        subject = f"Security Alert: {incident['severity'].upper()} - {incident['id']}"
        
        body = f"""
        Security Incident Alert
        
        Incident ID: {incident['id']}
        Severity: {incident['severity'].upper()}
        Type: {incident['type']}
        Description: {incident['description']}
        Source: {incident['source']}
        Created: {incident['created_at']}
        
        Details:
        {json.dumps(incident['details'], indent=2)}
        
        Please investigate immediately.
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {str(e)}")
    
    def send_slack_alert(self, incident: Dict[str, Any]):
        """Send Slack alert"""
        if not self.slack_webhook:
            return
        
        color = {
            'critical': '#ff0000',
            'high': '#ff6600',
            'medium': '#ffcc00',
            'low': '#00cc00'
        }.get(incident['severity'], '#cccccc')
        
        payload = {
            'attachments': [
                {
                    'color': color,
                    'title': f'Security Alert: {incident["severity"].upper()} - {incident["id"]}',
                    'fields': [
                        {'title': 'Type', 'value': incident['type'], 'short': True},
                        {'title': 'Severity', 'value': incident['severity'].upper(), 'short': True},
                        {'title': 'Description', 'value': incident['description'], 'short': False},
                        {'title': 'Source', 'value': incident['source'], 'short': True},
                        {'title': 'Created', 'value': incident['created_at'], 'short': True}
                    ],
                    'footer': 'Security Alert System',
                    'ts': int(datetime.now().timestamp())
                }
            ]
        }
        
        try:
            requests.post(self.slack_webhook, json=payload)
        except Exception as e:
            logging.error(f"Failed to send Slack alert: {str(e)}")

# Global alert manager instance
alert_manager = SecurityAlertManager()
```

## 📊 Security Metrics

### 1. Security KPIs

#### Security Dashboard
```python
# backend/security/metrics.py
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SecurityMetrics:
    def __init__(self):
        self.metrics = {
            'scan_results': [],
            'incidents': [],
            'vulnerabilities': [],
            'compliance_score': 0
        }
    
    def add_scan_result(self, tool: str, results: Dict[str, Any]):
        """Add scan result to metrics"""
        self.metrics['scan_results'].append({
            'tool': tool,
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
    
    def calculate_security_score(self) -> float:
        """Calculate overall security score"""
        if not self.metrics['scan_results']:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        weights = {
            'bandit': 0.3,
            'semgrep': 0.3,
            'snyk': 0.2,
            'npm_audit': 0.2
        }
        
        for scan in self.metrics['scan_results']:
            tool = scan['tool']
            results = scan['results']
            
            if tool in weights:
                score = self._calculate_tool_score(results)
                total_score += score * weights[tool]
                total_weight += weights[tool]
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_tool_score(self, results: Dict[str, Any]) -> float:
        """Calculate score for a specific tool"""
        total_issues = results.get('total_issues', 0)
        critical_issues = results.get('critical_issues', 0)
        high_issues = results.get('high_issues', 0)
        
        # Base score starts at 100
        score = 100.0
        
        # Deduct points for issues
        score -= critical_issues * 20
        score -= high_issues * 10
        score -= (total_issues - critical_issues - high_issues) * 2
        
        return max(0.0, score)
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate security metrics report"""
        return {
            'generated_at': datetime.now().isoformat(),
            'security_score': self.calculate_security_score(),
            'total_incidents': len(self.metrics['incidents']),
            'active_incidents': len([i for i in self.metrics['incidents'] if i['status'] == 'open']),
            'scan_summary': self._generate_scan_summary(),
            'trend_analysis': self._generate_trend_analysis()
        }
    
    def _generate_scan_summary(self) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {}
        
        for scan in self.metrics['scan_results']:
            tool = scan['tool']
            results = scan['results']
            
            if tool not in summary:
                summary[tool] = {
                    'total_scans': 0,
                    'total_issues': 0,
                    'critical_issues': 0,
                    'high_issues': 0,
                    'last_scan': scan['timestamp']
                }
            
            summary[tool]['total_scans'] += 1
            summary[tool]['total_issues'] += results.get('total_issues', 0)
            summary[tool]['critical_issues'] += results.get('critical_issues', 0)
            summary[tool]['high_issues'] += results.get('high_issues', 0)
        
        return summary
    
    def _generate_trend_analysis(self) -> Dict[str, Any]:
        """Generate trend analysis"""
        # Analyze last 30 days of scans
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_scans = [
            scan for scan in self.metrics['scan_results']
            if datetime.fromisoformat(scan['timestamp']) > thirty_days_ago
        ]
        
        if not recent_scans:
            return {'trend': 'insufficient_data'}
        
        # Calculate trend
        first_half = recent_scans[:len(recent_scans)//2]
        second_half = recent_scans[len(recent_scans)//2:]
        
        first_half_issues = sum(scan['results'].get('total_issues', 0) for scan in first_half)
        second_half_issues = sum(scan['results'].get('total_issues', 0) for scan in second_half)
        
        if second_half_issues < first_half_issues:
            trend = 'improving'
        elif second_half_issues > first_half_issues:
            trend = 'degrading'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'first_half_issues': first_half_issues,
            'second_half_issues': second_half_issues,
            'total_scans': len(recent_scans)
        }

# Global metrics instance
security_metrics = SecurityMetrics()
```

## 📚 Best Practices

### 1. Security Scanning

1. **Regular Scanning**: Schedule regular security scans
2. **Multiple Tools**: Use multiple security scanning tools
3. **Comprehensive Coverage**: Scan all code and dependencies
4. **Automated Integration**: Integrate scanning into CI/CD
5. **Result Analysis**: Analyze and act on scan results

### 2. Incident Management

1. **Quick Response**: Respond quickly to security incidents
2. **Proper Documentation**: Document all incidents and responses
3. **Root Cause Analysis**: Find and fix root causes
4. **Communication**: Communicate incidents to stakeholders
5. **Prevention**: Learn from incidents to prevent future ones

### 3. Continuous Improvement

1. **Regular Reviews**: Regularly review security processes
2. **Tool Updates**: Keep security tools updated
3. **Training**: Train team on security best practices
4. **Metrics**: Track and analyze security metrics
5. **Compliance**: Maintain compliance with security standards

---

*For authentication information, see [authentication.md](authentication.md).*
