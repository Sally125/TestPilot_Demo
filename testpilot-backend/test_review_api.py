"""端到端测试：评审报告功能"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import GeneratedCase, FeaturePoint

client = TestClient(app)


class TestReviewAPI:
    """评审API端到端测试"""

    def test_review_with_valid_cases_and_feature_points(self):
        """正常测试：使用有效的测试用例和功能点进行评审"""
        test_cases = [
            GeneratedCase(
                title="待办事项添加功能",
                module="todo_operations",
                priority="P0",
                precondition="页面已加载",
                steps=["输入内容", "点击添加"],
                expected="待办项显示在列表中",
                script="""import { test, expect } from '@playwright/test';

test.describe('TodoMVC-待办事项添加', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });
  });

  test('正常添加待办', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('测试任务');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.getByText('测试任务')).toBeVisible();
  });

  test('空输入不添加待办', async ({ page }) => {
    await page.getByPlaceholder('What needs to be done?').fill('');
    await page.getByPlaceholder('What needs to be done?').press('Enter');
    await expect(page.locator('.todo-list li')).toHaveCount(0);
  });
});""",
                stability_score=90,
            )
        ]

        feature_points = [
            FeaturePoint(
                name="待办事项添加",
                priority="P0",
                test_dimensions=["功能测试", "边界值测试"],
                business_logic="用户输入内容后按回车，待办事项被添加到列表",
                risk_hint="需要验证空输入和特殊字符处理",
            )
        ]

        response = client.post(
            "/api/review",
            json={
                "cases": [c.model_dump() for c in test_cases],
                "feature_points": [fp.model_dump() for fp in feature_points],
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "overall_score" in data
        assert isinstance(data["overall_score"], int)
        assert 0 <= data["overall_score"] <= 100

        assert "coverage_score" in data
        assert isinstance(data["coverage_score"], int)
        assert 0 <= data["coverage_score"] <= 100

        assert "completeness_score" in data
        assert isinstance(data["completeness_score"], int)
        assert 0 <= data["completeness_score"] <= 100

        assert "executability_score" in data
        assert isinstance(data["executability_score"], int)
        assert 0 <= data["executability_score"] <= 100

        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) <= 3

        assert "summary" in data
        assert isinstance(data["summary"], str)

    def test_review_with_multiple_cases(self):
        """正常测试：多个测试用例的评审"""
        test_cases = [
            GeneratedCase(
                title="待办事项添加",
                module="todo_operations",
                priority="P0",
                precondition="页面已加载",
                steps=["输入内容", "按回车"],
                expected="待办项显示",
                script="import { test, expect } from '@playwright/test';\n\ntest.describe('TodoMVC-添加', () => {\n  test.beforeEach(async ({ page }) => {\n    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });\n  });\n  test('添加待办', async ({ page }) => {\n    await page.getByPlaceholder('What needs to be done?').fill('Test');\n    await page.getByPlaceholder('What needs to be done?').press('Enter');\n    await expect(page.getByText('Test')).toBeVisible();\n  });\n});",
                stability_score=85,
            ),
            GeneratedCase(
                title="待办事项删除",
                module="todo_operations",
                priority="P1",
                precondition="存在待办项",
                steps=["点击删除按钮"],
                expected="待办项被删除",
                script="import { test, expect } from '@playwright/test';\n\ntest.describe('TodoMVC-删除', () => {\n  test.beforeEach(async ({ page }) => {\n    await page.goto('https://demo.playwright.dev/todomvc/', { waitUntil: 'domcontentloaded' });\n  });\n  test('删除待办', async ({ page }) => {\n    await page.getByPlaceholder('What needs to be done?').fill('Test');\n    await page.getByPlaceholder('What needs to be done?').press('Enter');\n    await page.getByRole('button', { name: 'Delete' }).click();\n    await expect(page.getByText('Test')).not.toBeVisible();\n  });\n});",
                stability_score=80,
            ),
        ]

        feature_points = [
            FeaturePoint(
                name="待办事项添加",
                priority="P0",
                test_dimensions=["功能测试"],
                business_logic="添加待办",
                risk_hint="",
            ),
            FeaturePoint(
                name="待办事项删除",
                priority="P1",
                test_dimensions=["功能测试"],
                business_logic="删除待办",
                risk_hint="",
            ),
        ]

        response = client.post(
            "/api/review",
            json={
                "cases": [c.model_dump() for c in test_cases],
                "feature_points": [fp.model_dump() for fp in feature_points],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert 0 <= data["overall_score"] <= 100
        assert len(data["suggestions"]) <= 3

    def test_review_with_empty_cases(self):
        """边界测试：空用例列表"""
        response = client.post(
            "/api/review",
            json={
                "cases": [],
                "feature_points": [
                    FeaturePoint(
                        name="测试功能",
                        priority="P0",
                        test_dimensions=["功能测试"],
                        business_logic="",
                        risk_hint="",
                    ).model_dump()
                ],
            },
        )

        assert response.status_code == 400 or response.status_code == 200

    def test_review_with_empty_feature_points(self):
        """边界测试：空功能点列表"""
        test_cases = [
            GeneratedCase(
                title="测试用例",
                module="test",
                priority="P1",
                precondition="",
                steps=[],
                expected="",
                script="import { test, expect } from '@playwright/test';\n\ntest.describe('Test', () => {\n  test('test', async ({ page }) => {\n    await expect(page).toHaveURL('http://localhost');\n  });\n});",
                stability_score=50,
            )
        ]

        response = client.post(
            "/api/review",
            json={
                "cases": [c.model_dump() for c in test_cases],
                "feature_points": [],
            },
        )

        assert response.status_code == 400 or response.status_code == 200

    def test_review_with_invalid_json_payload(self):
        """异常测试：无效的JSON格式"""
        response = client.post(
            "/api/review",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422

    def test_review_with_missing_fields(self):
        """异常测试：缺少必填字段"""
        response = client.post(
            "/api/review",
            json={"cases": []},
        )

        assert response.status_code == 422

    def test_review_score_calculation_logic(self):
        """验证评分逻辑：综合评分应基于各维度权重"""
        test_cases = [
            GeneratedCase(
                title="完整测试用例",
                module="test",
                priority="P0",
                precondition="",
                steps=["步骤1", "步骤2"],
                expected="预期结果",
                script="import { test, expect } from '@playwright/test';\n\ntest.describe('Complete', () => {\n  test.beforeEach(async ({ page }) => {\n    await page.goto('http://localhost', { waitUntil: 'domcontentloaded' });\n  });\n  test('正常流程', async ({ page }) => {\n    await expect(page).toBeVisible();\n  });\n  test('异常流程', async ({ page }) => {\n    await expect(page).toBeVisible();\n  });\n});",
                stability_score=90,
            )
        ]

        feature_points = [
            FeaturePoint(
                name="完整功能",
                priority="P0",
                test_dimensions=["功能测试", "边界值测试", "异常输入测试"],
                business_logic="完整的业务逻辑",
                risk_hint="",
            )
        ]

        response = client.post(
            "/api/review",
            json={
                "cases": [c.model_dump() for c in test_cases],
                "feature_points": [fp.model_dump() for fp in feature_points],
            },
        )

        assert response.status_code == 200
        data = response.json()

        coverage = data["coverage_score"]
        completeness = data["completeness_score"]
        executability = data["executability_score"]
        overall = data["overall_score"]

        expected_overall = int(coverage * 0.4 + completeness * 0.3 + executability * 0.3)
        assert abs(overall - expected_overall) <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])