#!/usr/bin/env python3
"""
Generate Human-Readable Diagnostic Report
Creates a comprehensive markdown report from diagnostic results
"""
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Template


def load_diagnostics(file_path: str) -> Dict[str, Any]:
    """Load diagnostics from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)


def generate_report(diagnostics: Dict[str, Any]) -> str:
    """Generate markdown report from diagnostics"""
    
    template = Template("""
# 🔍 Test Failure Diagnostics Report

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | {{ diagnostics.total_tests }} |
| **Passed** | {{ diagnostics.passed_tests }} |
| **Failed** | {{ diagnostics.failed_tests }} |
| **Success Rate** | {{ "%.1f"|format((diagnostics.passed_tests / diagnostics.total_tests * 100) if diagnostics.total_tests > 0 else 0) }}% |
| **Risk Level** | {{ diagnostics.risk_assessment.upper() }} |
| **Confidence Score** | {{ "%.1f"|format(diagnostics.confidence_score * 100) }}% |

## 🎯 Root Causes

{% for cause in diagnostics.root_causes %}
- **{{ cause }}**
{% endfor %}

## 🚨 Test Failures

{% for failure in diagnostics.failures %}
### ❌ {{ failure.test_name }}

**File:** `{{ failure.file_path }}:{{ failure.line_number }}`  
**Category:** {{ failure.category }}  
**Severity:** {{ failure.severity }}  
**Risk:** {{ failure.risk_level }}

**Error Message:**
```
{{ failure.error_message }}
```

**Suggested Fix:**
> {{ failure.suggested_fix }}

---
{% endfor %}

## 🔧 Recommended Actions

{% for action in diagnostics.suggested_actions %}
{{ loop.index }}. {{ action }}
{% endfor %}

## 📋 Risk Assessment

**Overall Risk Level:** {{ diagnostics.risk_assessment.upper() }}

### Risk Breakdown:
{% for failure in diagnostics.failures %}
- **{{ failure.test_name }}**: {{ failure.risk_level }} risk ({{ failure.severity }} severity)
{% endfor %}

## 🎯 Next Steps

1. **Immediate Actions** (High Priority):
   {% for failure in diagnostics.failures %}
   {% if failure.severity == 'critical' %}
   - Fix {{ failure.test_name }}: {{ failure.suggested_fix }}
   {% endif %}
   {% endfor %}

2. **Short-term Actions** (Medium Priority):
   {% for failure in diagnostics.failures %}
   {% if failure.severity == 'high' %}
   - Address {{ failure.test_name }}: {{ failure.suggested_fix }}
   {% endif %}
   {% endfor %}

3. **Long-term Actions** (Low Priority):
   {% for failure in diagnostics.failures %}
   {% if failure.severity in ['medium', 'low'] %}
   - Review {{ failure.test_name }}: {{ failure.suggested_fix }}
   {% endif %}
   {% endfor %}

## 🔗 Additional Resources

- [Development Guide](DEV_README.md)
- [Testing Documentation](backend/tests/README.md)
- [API Documentation](http://localhost:8000/docs)

---

**Generated:** {{ diagnostics.timestamp }}  
**Commit:** {{ diagnostics.commit_sha }}  
**Branch:** {{ diagnostics.branch }}  
**Repository:** {{ diagnostics.repository }}
""")
    
    return template.render(diagnostics=diagnostics)


def categorize_failures_by_severity(failures: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize failures by severity"""
    categories = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': []
    }
    
    for failure in failures:
        severity = failure.get('severity', 'low')
        if severity in categories:
            categories[severity].append(failure)
    
    return categories


def generate_fix_suggestions(failures: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Generate categorized fix suggestions"""
    suggestions = {
        'import_fixes': [],
        'database_fixes': [],
        'config_fixes': [],
        'logic_fixes': [],
        'other_fixes': []
    }
    
    for failure in failures:
        category = failure.get('category', 'unknown')
        fix = failure.get('suggested_fix', '')
        
        if category == 'import_error':
            suggestions['import_fixes'].append(fix)
        elif category == 'database_error':
            suggestions['database_fixes'].append(fix)
        elif category == 'configuration_error':
            suggestions['config_fixes'].append(fix)
        elif category == 'logic_error':
            suggestions['logic_fixes'].append(fix)
        else:
            suggestions['other_fixes'].append(fix)
    
    # Remove duplicates
    for key in suggestions:
        suggestions[key] = list(set(suggestions[key]))
    
    return suggestions


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate Diagnostic Report')
    parser.add_argument('--diagnostics', required=True, help='Path to diagnostics JSON file')
    parser.add_argument('--output', required=True, help='Output markdown file')
    
    args = parser.parse_args()
    
    # Load diagnostics
    diagnostics = load_diagnostics(args.diagnostics)
    
    # Generate report
    report = generate_report(diagnostics)
    
    # Save report
    with open(args.output, 'w') as f:
        f.write(report)
    
    print(f"✅ Diagnostic report generated: {args.output}")
    print(f"📊 Analyzed {diagnostics['failed_tests']} test failures")
    print(f"🎯 Risk level: {diagnostics['risk_assessment']}")


if __name__ == "__main__":
    main()








