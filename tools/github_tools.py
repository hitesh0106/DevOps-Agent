"""
DevOps Agent — GitHub Tools
"""

import json
from tools.base import BaseTool
from config.constants import ToolCategory, RiskLevel, SIMULATION_RESPONSES


class ListRepos(BaseTool):
    name = "list_repos"
    description = "List GitHub repositories in the organization"
    category = ToolCategory.CICD
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"org": "string (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            repos = SIMULATION_RESPONSES["github"]["repos"]
            return json.dumps({"repos": repos, "count": len(repos)})
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        org = kwargs.get("org", settings.github.github_default_org)
        repos = [r.full_name for r in g.get_organization(org).get_repos()]
        return json.dumps({"repos": repos, "count": len(repos)})


class GetPRDetails(BaseTool):
    name = "get_pr_details"
    description = "Get details of a pull request"
    category = ToolCategory.CICD
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"repo": "string", "pr_number": "integer"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "title": "Fix API timeout in /health endpoint",
                "state": "open", "author": "dev-user",
                "files_changed": 3, "additions": 42, "deletions": 12,
                "reviews": [{"user": "reviewer1", "state": "approved"}],
                "ci_status": "passing",
            })
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        repo = g.get_repo(kwargs["repo"])
        pr = repo.get_pull(kwargs["pr_number"])
        return json.dumps({"title": pr.title, "state": pr.state, "author": pr.user.login})


class CreatePullRequest(BaseTool):
    name = "create_pull_request"
    description = "Create a new pull request"
    category = ToolCategory.CICD
    risk_level = RiskLevel.MEDIUM
    parameters_schema = '{"repo": "string", "title": "string", "body": "string", "head": "string", "base": "string"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"pr_number": 42, "url": "https://github.com/org/repo/pull/42", "status": "created"})
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        repo = g.get_repo(kwargs["repo"])
        pr = repo.create_pull(title=kwargs["title"], body=kwargs.get("body", ""), head=kwargs["head"], base=kwargs.get("base", "main"))
        return json.dumps({"pr_number": pr.number, "url": pr.html_url})


class GetCIStatus(BaseTool):
    name = "get_ci_status"
    description = "Check GitHub Actions CI pipeline status for a repository"
    category = ToolCategory.CICD
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"repo": "string"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "repo": kwargs.get("repo", "main-app"),
                "status": "passing",
                "workflows": [
                    {"name": "CI", "status": "completed", "conclusion": "success", "run_number": 187},
                    {"name": "Security Scan", "status": "completed", "conclusion": "success", "run_number": 45},
                ],
                "last_run": "2 hours ago",
            })
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        repo = g.get_repo(kwargs["repo"])
        runs = list(repo.get_workflow_runs()[:5])
        return json.dumps({"workflows": [{"name": r.name, "status": r.status, "conclusion": r.conclusion} for r in runs]})


class GetFailingTests(BaseTool):
    name = "get_failing_tests"
    description = "Extract failing test details from CI logs"
    category = ToolCategory.CICD
    risk_level = RiskLevel.SAFE
    parameters_schema = '{"repo": "string", "run_id": "integer (optional)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({
                "total_tests": 156, "passed": 154, "failed": 2,
                "failures": [
                    {"test": "test_api_health", "error": "AssertionError: expected 200, got 500", "file": "tests/test_api.py:42"},
                    {"test": "test_db_connection", "error": "ConnectionRefusedError: port 5432", "file": "tests/test_db.py:18"},
                ],
            })
        return json.dumps({"message": "Requires GitHub API implementation for log parsing"})


class PostComment(BaseTool):
    name = "post_comment"
    description = "Post a comment on a GitHub issue or pull request"
    category = ToolCategory.CICD
    risk_level = RiskLevel.LOW
    parameters_schema = '{"repo": "string", "issue_number": "integer", "body": "string"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "commented", "issue": kwargs.get("issue_number", 1)})
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        repo = g.get_repo(kwargs["repo"])
        issue = repo.get_issue(kwargs["issue_number"])
        comment = issue.create_comment(kwargs["body"])
        return json.dumps({"comment_id": comment.id})


class MergePR(BaseTool):
    name = "merge_pr"
    description = "Merge a pull request"
    category = ToolCategory.CICD
    risk_level = RiskLevel.HIGH
    parameters_schema = '{"repo": "string", "pr_number": "integer", "merge_method": "string (merge|squash|rebase)"}'

    def execute(self, **kwargs):
        if self.simulation_mode:
            return json.dumps({"status": "merged", "pr_number": kwargs.get("pr_number", 42), "sha": "abc123def456"})
        from github import Github
        from config.settings import settings
        g = Github(settings.github.github_token)
        repo = g.get_repo(kwargs["repo"])
        pr = repo.get_pull(kwargs["pr_number"])
        pr.merge(merge_method=kwargs.get("merge_method", "squash"))
        return json.dumps({"status": "merged", "pr_number": pr.number})
