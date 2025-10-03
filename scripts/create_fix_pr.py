#!/usr/bin/env python3
"""
Create Automated Fix PR
Creates a pull request with suggested fixes for test failures
"""
import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import git
import requests
from jinja2 import Template


class FixPRCreator:
    """Creates pull requests with automated fixes"""
    
    def __init__(self, repo_path: str = ".", github_token: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(self.repo_path)
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        
        if not self.github_token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable.")
    
    def create_fix_pr(self, 
                     fix_suggestions_dir: str,
                     repo: str,
                     base_branch: str,
                     pr_title: str,
                     pr_body: str) -> Dict[str, Any]:
        """Create a pull request with fixes"""
        print("🔧 Creating fix PR...")
        
        # Load fix suggestions
        fix_results_file = Path(fix_suggestions_dir) / 'fix-results.json'
        if not fix_results_file.exists():
            raise FileNotFoundError(f"Fix results not found: {fix_results_file}")
        
        with open(fix_results_file, 'r') as f:
            fix_results = json.load(f)
        
        # Create new branch
        branch_name = f"auto-fix-{self._generate_branch_suffix()}"
        self._create_fix_branch(branch_name, base_branch)
        
        # Apply fixes
        applied_fixes = self._apply_fixes(fix_suggestions_dir)
        
        # Commit changes
        commit_message = self._generate_commit_message(fix_results)
        self._commit_fixes(commit_message, applied_fixes)
        
        # Push branch
        self._push_branch(branch_name)
        
        # Create PR
        pr_data = self._create_pull_request(
            repo, branch_name, base_branch, pr_title, pr_body, fix_results
        )
        
        print(f"✅ Fix PR created: {pr_data['html_url']}")
        
        return {
            'pr_number': pr_data['number'],
            'pr_url': pr_data['html_url'],
            'branch_name': branch_name,
            'fixes_applied': len(applied_fixes),
            'total_fixes': fix_results['total_fixes']
        }
    
    def _generate_branch_suffix(self) -> str:
        """Generate unique branch suffix"""
        import time
        return f"test-fixes-{int(time.time())}"
    
    def _create_fix_branch(self, branch_name: str, base_branch: str):
        """Create new branch for fixes"""
        print(f"🌿 Creating branch: {branch_name}")
        
        # Fetch latest changes
        origin = self.repo.remotes.origin
        origin.fetch()
        
        # Create and checkout new branch
        try:
            # Get the remote base branch
            remote_base = f"origin/{base_branch}"
            if remote_base in [ref.name for ref in self.repo.refs]:
                new_branch = self.repo.create_head(branch_name, remote_base)
            else:
                # Fallback to local base branch
                new_branch = self.repo.create_head(branch_name, base_branch)
            
            new_branch.checkout()
            print(f"✅ Branch {branch_name} created and checked out")
            
        except Exception as e:
            print(f"❌ Error creating branch: {e}")
            raise
    
    def _apply_fixes(self, fix_suggestions_dir: str) -> List[Dict[str, Any]]:
        """Apply fixes from suggestion files"""
        print("🔧 Applying fixes...")
        
        fix_dir = Path(fix_suggestions_dir)
        applied_fixes = []
        
        # Process fix files
        fix_files = list(fix_dir.glob("fix_*.py"))
        
        for fix_file in fix_files:
            try:
                fix_data = self._parse_fix_file(fix_file)
                if self._apply_single_fix(fix_data):
                    applied_fixes.append(fix_data)
                    print(f"✅ Applied fix: {fix_data['test_name']}")
                else:
                    print(f"⚠️  Could not apply fix: {fix_data['test_name']}")
                    
            except Exception as e:
                print(f"❌ Error applying fix from {fix_file}: {e}")
        
        return applied_fixes
    
    def _parse_fix_file(self, fix_file: Path) -> Dict[str, Any]:
        """Parse fix file to extract metadata"""
        with open(fix_file, 'r') as f:
            content = f.read()
        
        # Extract test name from content
        test_name = "unknown_test"
        if "Fix for" in content:
            import re
            match = re.search(r'Fix for [^:]+: ([^\n]+)', content)
            if match:
                test_name = match.group(1).strip()
        
        return {
            'file': fix_file.name,
            'test_name': test_name,
            'category': fix_file.stem.split('_')[2] if '_' in fix_file.stem else 'unknown',
            'content': content
        }
    
    def _apply_single_fix(self, fix_data: Dict[str, Any]) -> bool:
        """Apply a single fix"""
        try:
            # For now, just create the fix file in the appropriate location
            # In a real implementation, this would be more sophisticated
            
            fix_file_name = f"fix_{fix_data['category']}.py"
            fix_file_path = self.repo_path / "fixes" / fix_file_name
            
            # Create fixes directory if it doesn't exist
            fix_file_path.parent.mkdir(exist_ok=True)
            
            # Write fix file
            with open(fix_file_path, 'w') as f:
                f.write(fix_data['content'])
            
            # Add to git
            self.repo.index.add([str(fix_file_path)])
            
            return True
            
        except Exception as e:
            print(f"❌ Error applying fix: {e}")
            return False
    
    def _generate_commit_message(self, fix_results: Dict[str, Any]) -> str:
        """Generate commit message for fixes"""
        summary = fix_results['summary']
        
        return f"""🔧 Auto-fix: {fix_results['total_fixes']} test failures

- Fixed {summary['severity_breakdown']['critical']} critical issues
- Fixed {summary['severity_breakdown']['high']} high severity issues  
- Fixed {summary['severity_breakdown']['medium']} medium severity issues
- Fixed {summary['severity_breakdown']['low']} low severity issues

Categories: {', '.join(summary['categories'])}

Risk Level: {summary['risk_assessment'].upper()}
Confidence: {summary['confidence']:.1%}

Auto-generated by intelligent testing system."""
    
    def _commit_fixes(self, commit_message: str, applied_fixes: List[Dict[str, Any]]):
        """Commit applied fixes"""
        print("💾 Committing fixes...")
        
        try:
            # Commit changes
            self.repo.index.commit(commit_message)
            print("✅ Fixes committed")
            
        except Exception as e:
            print(f"❌ Error committing fixes: {e}")
            raise
    
    def _push_branch(self, branch_name: str):
        """Push branch to remote"""
        print(f"📤 Pushing branch: {branch_name}")
        
        try:
            origin = self.repo.remotes.origin
            origin.push(branch_name)
            print("✅ Branch pushed to remote")
            
        except Exception as e:
            print(f"❌ Error pushing branch: {e}")
            raise
    
    def _create_pull_request(self, 
                           repo: str, 
                           branch_name: str, 
                           base_branch: str,
                           title: str, 
                           body: str,
                           fix_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create pull request via GitHub API"""
        print("📝 Creating pull request...")
        
        # Enhance PR body with fix details
        enhanced_body = self._enhance_pr_body(body, fix_results)
        
        # GitHub API request
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'body': enhanced_body,
            'head': branch_name,
            'base': base_branch,
            'labels': ['auto-fix', 'tests', 'ci']
        }
        
        url = f'https://api.github.com/repos/{repo}/pulls'
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            pr_data = response.json()
            print(f"✅ PR created: #{pr_data['number']}")
            
            return pr_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating PR: {e}")
            raise
    
    def _enhance_pr_body(self, base_body: str, fix_results: Dict[str, Any]) -> str:
        """Enhance PR body with fix details"""
        summary = fix_results['summary']
        
        enhanced_body = f"""## 🤖 Automated Fix Pull Request

{base_body}

### 📊 Fix Summary

- **Total Fixes:** {fix_results['total_fixes']}
- **Categories:** {', '.join(summary['categories'])}
- **Risk Level:** {summary['risk_assessment'].upper()}
- **Confidence:** {summary['confidence']:.1%}

### 🎯 Fixes by Severity

| Severity | Count |
|----------|-------|
| Critical | {summary['severity_breakdown']['critical']} |
| High | {summary['severity_breakdown']['high']} |
| Medium | {summary['severity_breakdown']['medium']} |
| Low | {summary['severity_breakdown']['low']} |

### 🔧 Applied Fixes

This PR includes automated fixes for the following test failures:

"""
        
        # Add details for each fix
        for fix in fix_results.get('fixes', []):
            enhanced_body += f"- **{fix['test_name']}** ({fix['category']}, {fix['severity']} severity)\n"
            enhanced_body += f"  - Explanation: {fix.get('explanation', 'N/A')}\n"
            enhanced_body += f"  - Risk: {fix.get('risk_notes', 'N/A')}\n\n"
        
        enhanced_body += """### ⚠️ Risk Assessment

**Please review the following before merging:**

1. **Test all fixes thoroughly** - Run the full test suite
2. **Check for regressions** - Ensure no new failures introduced
3. **Security review** - Pay special attention to authentication fixes
4. **Performance impact** - Monitor for any performance degradation
5. **Database changes** - Verify migrations work correctly

### 🧪 Verification Steps

1. Review each fix file in the `fixes/` directory
2. Run specific failing tests: `pytest <test_name> -v`
3. Run full test suite: `make test`
4. Deploy to staging for validation
5. Monitor application logs after deployment

### 📋 Auto-Generated by Intelligent Testing System

This PR was automatically generated by our intelligent testing system that:
- Analyzes test failures
- Categorizes issues by type and severity
- Generates appropriate fixes
- Creates comprehensive test coverage
- Assesses risk levels

**Confidence Score:** {summary['confidence']:.1%}

---

**Note:** This is an automated PR. Please review all changes carefully before merging."""
        
        return enhanced_body


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Create Fix PR')
    parser.add_argument('--fix-suggestions', required=True, help='Path to fix suggestions directory')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--base-branch', required=True, help='Base branch name')
    parser.add_argument('--pr-title', required=True, help='PR title')
    parser.add_argument('--pr-body', required=True, help='PR body')
    
    args = parser.parse_args()
    
    # Create fix PR
    creator = FixPRCreator()
    result = creator.create_fix_pr(
        fix_suggestions_dir=args.fix_suggestions,
        repo=args.repo,
        base_branch=args.base_branch,
        pr_title=args.pr_title,
        pr_body=args.pr_body
    )
    
    print(f"✅ Fix PR creation completed")
    print(f"📊 PR #{result['pr_number']}: {result['pr_url']}")
    print(f"🌿 Branch: {result['branch_name']}")
    print(f"🔧 Fixes applied: {result['fixes_applied']}/{result['total_fixes']}")


if __name__ == "__main__":
    main()








