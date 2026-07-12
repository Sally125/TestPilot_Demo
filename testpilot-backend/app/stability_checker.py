import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class StabilityChecker:
    def __init__(self):
        self.issues: List[Dict] = []
        self.scores: Dict[str, int] = {}
        self.checks: Dict[str, Dict] = {}

    def analyze(self, script_content: str, case_title: str = "") -> Dict:
        self.issues = []
        self.scores = {}
        self.checks = {}

        self._check_selector_strength(script_content)
        self._check_login_state(script_content)
        self._check_wait_strategy(script_content)
        self._check_dynamic_data(script_content)
        self._check_exception_handling(script_content)

        overall_score = self._calculate_overall_score()

        return {
            "case_title": case_title,
            "checks": self.checks,
            "issues": self.issues,
            "scores": self.scores,
            "overall_score": overall_score
        }

    def _check_selector_strength(self, script: str):
        check_name = "selector_stability"
        issues = []
        risk_count = 0
        fixed_count = 0

        weak_selectors = [
            (r'\.locator\(["\']\.css-[a-zA-Z0-9_-]+["\']\)', "CSS哈希选择器", "应使用getByTestId或getByRole"),
            (r'\.locator\(["\'].*nth-child\([0-9]+\)[^\)]*["\']\)', "nth-child选择器", "应使用getByRole或getByTestId"),
            (r'\.locator\(["\']/html/.*["\']\)', "绝对XPath", "应使用相对路径或语义化选择器"),
            (r'\.locator\(["\']//\*\[.*@id=["\'][^"\']+["\']\][^\)]*["\']\)', "ID XPath", "应使用getByTestId"),
            (r'\.locator\(["\']\.btn-[a-zA-Z0-9_-]+["\']\)', "样式类选择器", "应使用getByRole或getByLabel"),
        ]

        strong_selectors = [
            'getByRole',
            'getByLabel',
            'getByPlaceholder',
            'getByText',
            'getByTestId',
            'getByAltText',
            'getByTitle',
        ]

        for pattern, selector_type, suggestion in weak_selectors:
            matches = re.findall(pattern, script)
            for match in matches[:5]:
                risk_count += 1
                issues.append({
                    "type": check_name,
                    "level": "warning",
                    "message": f"发现{selector_type}: {match[:50]}",
                    "suggestion": suggestion,
                    "auto_fix": True
                })

        strong_count = sum(script.count(s) for s in strong_selectors)

        if risk_count > 0:
            fixed_count = min(risk_count, strong_count)

        score = min(100, max(0, 70 + (strong_count - risk_count) * 6))
        self.scores[check_name] = score
        self.checks[check_name] = {
            "passed": score >= 75,
            "risk_count": risk_count,
            "fixed_count": fixed_count,
            "suggestion": "已自动优化" if fixed_count > 0 else "建议优化选择器"
        }
        self.issues.extend(issues)

    def _check_login_state(self, script: str):
        check_name = "login_state"
        issues = []

        login_patterns = [
            (r'page\.goto\(["\'].*login["\']', "登录页面"),
            (r'page\.goto\(["\'].*signin["\']', "登录页面"),
            (r'page\.goto\(["\'].*sign-up["\']', "注册页面"),
            (r'getByLabel\(["\'].*密码["\']\)', "密码输入"),
            (r'getByLabel\(["\'].*password["\']\)', "密码输入"),
        ]

        needs_login = False
        has_storage_state = 'storageState' in script

        for pattern, page_type in login_patterns:
            if re.search(pattern, script, re.IGNORECASE):
                needs_login = True
                break

        if needs_login and not has_storage_state:
            issues.append({
                "type": check_name,
                "level": "warning",
                "message": "检测到需要登录的页面操作",
                "suggestion": "建议在playwright.config中配置storageState注入登录态",
                "auto_fix": True
            })

        score = 100 if (not needs_login or has_storage_state) else 60
        self.scores[check_name] = score
        self.checks[check_name] = {
            "passed": score >= 80,
            "needs_login": needs_login,
            "has_storage_state": has_storage_state,
            "suggestion": "已自动注入" if needs_login and has_storage_state else ("需配置登录态" if needs_login else "无需登录")
        }
        self.issues.extend(issues)

    def _check_wait_strategy(self, script: str):
        check_name = "wait_strategy"
        issues = []
        bad_wait_count = 0

        bad_wait_patterns = [
            (r'waitForTimeout\([0-9]+\)', "硬编码waitForTimeout"),
            (r'page\.waitFor\([0-9]+[^\)]*\)', "硬编码page.waitFor"),
            (r'setTimeout\([^)]+\)', "setTimeout"),
            (r'await\s+new\s+Promise\(.*resolve.*[0-9]+', "Promise延时"),
        ]

        web_first_patterns = [
            'toBeVisible',
            'toBeEnabled',
            'toBeHidden',
            'toBeChecked',
            'toHaveText',
            'toHaveValue',
            'toHaveClass',
            'waitForURL',
            'waitForSelector',
            'waitForResponse',
            'waitForRequest',
        ]

        for pattern, wait_type in bad_wait_patterns:
            matches = re.findall(pattern, script)
            for match in matches[:5]:
                bad_wait_count += 1
                issues.append({
                    "type": check_name,
                    "level": "warning",
                    "message": f"发现{wait_type}: {match[:30]}",
                    "suggestion": "应替换为Web-First断言如toBeVisible/toHaveText等",
                    "auto_fix": True
                })

        web_first_count = sum(script.count(p) for p in web_first_patterns)

        score = min(100, max(0, 60 + (web_first_count - bad_wait_count) * 8))
        self.scores[check_name] = score
        self.checks[check_name] = {
            "passed": score >= 75,
            "bad_wait_count": bad_wait_count,
            "web_first_count": web_first_count,
            "suggestion": "已替换为auto-wait" if bad_wait_count > 0 and web_first_count > 0 else "建议使用Web-First断言"
        }
        self.issues.extend(issues)

    def _check_dynamic_data(self, script: str):
        check_name = "dynamic_data"
        issues = []

        hardcoded_patterns = [
            (r'fill\(["\'][a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}["\']\)', "硬编码邮箱"),
            (r'fill\(["\'][0-9]{11}["\']\)', "硬编码手机号"),
            (r'fill\(["\'][A-Za-z0-9]{8,}["\']\)', "硬编码密码/Token"),
            (r'fill\(["\'][a-zA-Z][a-zA-Z0-9_]{2,}["\']\)', "硬编码用户名"),
            (r'fill\(["\'][0-9]{4,}["\']\)', "硬编码数字（订单号等）"),
        ]

        faker_patterns = [
            'faker.',
            'generateRandom',
            'randomString',
            'uniqueId',
            'testData.',
        ]

        has_hardcoded = False
        has_faker = any(p in script for p in faker_patterns)

        for pattern, data_type in hardcoded_patterns:
            matches = re.findall(pattern, script)
            for match in matches[:3]:
                has_hardcoded = True
                issues.append({
                    "type": check_name,
                    "level": "info",
                    "message": f"发现{data_type}: {match[:40]}",
                    "suggestion": "建议使用Faker或测试数据工厂生成动态数据",
                    "auto_fix": False
                })

        score = 100 if (not has_hardcoded or has_faker) else 70
        self.scores[check_name] = score
        self.checks[check_name] = {
            "passed": score >= 80,
            "has_hardcoded": has_hardcoded,
            "has_faker": has_faker,
            "suggestion": "已配置Faker" if has_faker else ("需配置动态数据" if has_hardcoded else "无需配置")
        }
        self.issues.extend(issues)

    def _check_exception_handling(self, script: str):
        check_name = "exception_handling"
        issues = []

        risky_operations = [
            '.click()',
            '.fill()',
            'page.goto(',
            'page.reload(',
        ]

        try_catch_count = script.count('try {')
        retry_count = script.count('.retry(')

        risky_count = sum(script.count(op) for op in risky_operations)

        if risky_count > 2 and try_catch_count == 0 and retry_count == 0:
            issues.append({
                "type": check_name,
                "level": "info",
                "message": f"发现{risky_count}处风险操作，建议添加异常处理",
                "suggestion": "关键操作可包裹在try-catch中或使用retry机制",
                "auto_fix": False
            })

        score = min(100, max(0, 80 + try_catch_count * 10 + retry_count * 15))
        self.scores[check_name] = score
        self.checks[check_name] = {
            "passed": score >= 80,
            "risky_count": risky_count,
            "try_catch_count": try_catch_count,
            "suggestion": "已添加异常处理" if try_catch_count > 0 else "建议添加异常处理"
        }
        self.issues.extend(issues)

    def _calculate_overall_score(self) -> int:
        if not self.scores:
            return 0
        weights = {
            "selector_stability": 0.35,
            "login_state": 0.25,
            "wait_strategy": 0.25,
            "dynamic_data": 0.10,
            "exception_handling": 0.05,
        }
        total = 0
        total_weight = 0
        for name, score in self.scores.items():
            total += score * weights.get(name, 0.2)
            total_weight += weights.get(name, 0.2)
        return int(total / total_weight)

    def auto_fix(self, script_content: str) -> Tuple[str, List[Dict]]:
        fixes = []
        script = script_content

        script, fix1 = self._fix_selectors(script)
        fixes.extend(fix1)

        script, fix2 = self._fix_wait_strategy(script)
        fixes.extend(fix2)

        script, fix3 = self._fix_login_state(script)
        fixes.extend(fix3)

        return script, fixes

    def _fix_selectors(self, script: str) -> Tuple[str, List[Dict]]:
        fixes = []
        original_script = script

        script = re.sub(
            r'\.locator\(["\'](#[a-zA-Z0-9_-]+)["\']\)',
            r'.getByTestId(\1.replace("#", ""))',
            script
        )
        if script != original_script:
            fixes.append({
                "type": "selector_stability",
                "message": "已将ID选择器替换为getByTestId",
                "suggestion": "建议在页面元素上添加data-testid属性"
            })

        script = re.sub(
            r'\.locator\(["\']\.[a-zA-Z0-9_-]+["\']\)',
            r'.getByRole("button")',
            script
        )
        if script != original_script:
            fixes.append({
                "type": "selector_stability",
                "message": "已将类选择器替换为getByRole",
                "suggestion": "请根据实际元素类型调整getByRole参数"
            })

        return script, fixes

    def _fix_wait_strategy(self, script: str) -> Tuple[str, List[Dict]]:
        fixes = []
        original_script = script

        script = re.sub(
            r'await\s+page\.waitForTimeout\([0-9]+\)',
            '// 已移除硬编码等待，建议添加Web-First断言',
            script
        )

        script = re.sub(
            r'await\s+page\.waitFor\([0-9]+[^\)]*\)',
            '// 已移除硬编码等待，建议添加Web-First断言',
            script
        )

        if script != original_script:
            fixes.append({
                "type": "wait_strategy",
                "message": "已移除硬编码等待",
                "suggestion": "请在关键操作后添加await expect(...).toBeVisible()等断言"
            })

        return script, fixes

    def _fix_login_state(self, script: str) -> Tuple[str, List[Dict]]:
        fixes = []
        if 'storageState' not in script:
            if re.search(r'page\.goto\(["\'].*login["\']', script, re.IGNORECASE):
                fixes.append({
                    "type": "login_state",
                    "message": "检测到登录操作，建议配置storageState",
                    "suggestion": "在playwright.config.ts中添加use.storageState配置"
                })
        return script, fixes
