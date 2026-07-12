"""端到端测试：稳定性保障功能"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestStabilityAPI:
    """稳定性检查API端到端测试"""

    def test_check_project_stability(self):
        """正常测试：检查项目稳定性"""
        response = client.post(
            "/api/projects/1/stability/check-all"
        )

        assert response.status_code == 200
        data = response.json()

        assert "projectId" in data
        assert isinstance(data["projectId"], int)

        assert "caseCount" in data
        assert isinstance(data["caseCount"], int)

        assert "totalIssues" in data
        assert isinstance(data["totalIssues"], int)

        assert "scores" in data
        assert isinstance(data["scores"], dict)

        assert "overallScore" in data
        assert isinstance(data["overallScore"], int)
        assert 0 <= data["overallScore"] <= 100

        assert "checks" in data
        checks = data["checks"]
        assert isinstance(checks, dict)
        assert "selector_stability" in checks
        assert "login_state" in checks
        assert "wait_strategy" in checks
        assert "dynamic_data" in checks

        for key in ["selector_stability", "login_state", "wait_strategy", "dynamic_data"]:
            assert "label" in checks[key]
            assert "risk_count" in checks[key]
            assert "suggestion" in checks[key]
            assert "tag" in checks[key]

        assert "cases" in data
        assert isinstance(data["cases"], list)

    def test_check_project_not_found(self):
        """异常测试：项目不存在"""
        response = client.post(
            "/api/projects/999/stability/check-all"
        )

        assert response.status_code == 404

    def test_check_project_without_cases(self):
        """边界测试：项目没有测试用例"""
        response = client.post(
            "/api/projects/2/stability/check-all"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["caseCount"] == 0
        assert data["totalIssues"] == 0

    def test_check_project_returns_case_details(self):
        """验证返回每个用例的详细信息"""
        response = client.post(
            "/api/projects/1/stability/check-all"
        )

        assert response.status_code == 200
        data = response.json()

        if data["cases"] and len(data["cases"]) > 0:
            case = data["cases"][0]
            assert "id" in case
            assert "title" in case
            assert "module" in case
            assert "overall_score" in case
            assert "scores" in case
            assert "checks" in case
            assert "issues" in case

    def test_check_project_returns_issues(self):
        """验证返回问题列表"""
        response = client.post(
            "/api/projects/1/stability/check-all"
        )

        assert response.status_code == 200
        data = response.json()

        if data["cases"]:
            for case in data["cases"]:
                if case["issues"]:
                    for issue in case["issues"]:
                        assert "message" in issue
                        assert "suggestion" in issue
                        assert "type" in issue


class TestReviewAPI:
    """评审报告API端到端测试"""

    def test_generate_project_review(self):
        """正常测试：生成项目评审报告"""
        response = client.post(
            "/api/projects/1/review/generate"
        )

        assert response.status_code == 200
        data = response.json()

        assert "score" in data
        assert isinstance(data["score"], int)
        assert 0 <= data["score"] <= 100

        assert "subtitle" in data
        assert isinstance(data["subtitle"], str)

        assert "reqSource" in data

        assert "time" in data

        assert "model" in data

        assert "metrics" in data
        assert isinstance(data["metrics"], list)

        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_generate_review_without_cases(self):
        """异常测试：项目没有测试用例"""
        response = client.post(
            "/api/projects/2/review/generate"
        )

        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])