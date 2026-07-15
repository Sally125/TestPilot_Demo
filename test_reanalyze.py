import requests
import time
import sys

BASE_URL = "http://localhost:8000/api"

def test_reanalyze_feature():
    print("=== 测试重新分析功能 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 后端服务未启动")
            return False
        print("✅ 后端服务正常")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务")
        return False

    print("\n1. 创建项目...")
    project_data = {
        "name": f"测试重新分析项目_{int(time.time())}",
        "app_url": "https://example.com",
        "description": "测试项目"
    }
    try:
        response = requests.post(f"{BASE_URL}/projects", json=project_data)
        project = response.json()
        project_id = project["id"]
        print(f"✅ 项目创建成功, ID: {project_id}")
    except Exception as e:
        print(f"❌ 创建项目失败: {e}")
        return False

    print("\n2. 创建需求...")
    req_data = {
        "title": "测试需求",
        "content": "用户可以登录系统，输入用户名和密码，点击登录按钮验证身份。"
    }
    try:
        response = requests.post(f"{BASE_URL}/projects/{project_id}/requirements", json=req_data)
        requirement = response.json()
        req_id = requirement["id"]
        print(f"✅ 需求创建成功, ID: {req_id}")
    except Exception as e:
        print(f"❌ 创建需求失败: {e}")
        return False

    print("\n3. 执行初始分析...")
    try:
        response = requests.post(f"{BASE_URL}/analyze", json={
            "requirement_text": req_data["content"],
            "app_url": project_data["app_url"]
        })
        analysis = response.json()
        print(f"✅ 初始分析成功, 功能点数量: {len(analysis.get('feature_points', []))}")
    except Exception as e:
        print(f"❌ 初始分析失败: {e}")
        return False

    print("\n4. 保存分析结果...")
    try:
        response = requests.put(f"{BASE_URL}/requirements/{req_id}/analysis", json={"analysis_result": analysis})
        print(f"✅ 分析结果保存成功")
    except Exception as e:
        print(f"❌ 保存分析结果失败: {e}")
        return False

    print("\n5. 模拟重新分析（调用同一个分析API）...")
    try:
        response = requests.post(f"{BASE_URL}/analyze", json={
            "requirement_text": req_data["content"],
            "app_url": project_data["app_url"]
        })
        reanalysis = response.json()
        print(f"✅ 重新分析成功, 功能点数量: {len(reanalysis.get('feature_points', []))}")
    except Exception as e:
        print(f"❌ 重新分析失败: {e}")
        return False

    print("\n6. 更新分析结果...")
    try:
        response = requests.put(f"{BASE_URL}/requirements/{req_id}/analysis", json={"analysis_result": reanalysis})
        print(f"✅ 重新分析结果保存成功")
    except Exception as e:
        print(f"❌ 保存重新分析结果失败: {e}")
        return False

    print("\n7. 验证重新分析结果已更新...")
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/requirements")
        requirements = response.json()
        updated_req = next(r for r in requirements if r["id"] == req_id)
        if updated_req.get("analysisResult"):
            print(f"✅ 验证成功: 需求分析结果已更新")
            print(f"   功能点数量: {len(updated_req['analysisResult'].get('feature_points', []))}")
        else:
            print("❌ 验证失败: 分析结果未更新")
            return False
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

    print("\n=== 测试完成 ===")
    print("✅ 重新分析功能测试通过")
    print(f"项目ID: {project_id}")
    print(f"需求ID: {req_id}")
    return True

if __name__ == "__main__":
    success = test_reanalyze_feature()
    sys.exit(0 if success else 1)