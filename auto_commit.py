#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动GitHub提交脚本
实现每日自动提交和PR创建功能
"""

import os
import json
import time
import random
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
import hashlib
import base64
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO, GITHUB_EMAIL,
    COMMIT_MESSAGE_TEMPLATE, PR_TITLE_TEMPLATE, PR_BODY_TEMPLATE,
    DATA_DIR, LOG_FILE, MAIN_BRANCH, PR_BRANCH_PREFIX,
    GITHUB_API_BASE, REQUEST_TIMEOUT, MAX_RETRIES,
    validate_config
)

# 配置日志
def setup_logging(account_name='default'):
    """设置日志配置"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log_file = LOG_FILE.replace('.log', f'_{account_name}.log')
    
    # 为每个账号创建独立的logger
    logger_name = f'auto_commit_{account_name}'
    logger = logging.getLogger(logger_name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

class GitHubAutoCommit:
    """GitHub自动提交类"""
    
    def __init__(self, account_config: Dict[str, str] = None):
        if account_config:
            self.token = account_config['token']
            self.username = account_config['username']
            self.email = account_config['email']
            self.repo_name = account_config['repo']
            self.account_name = account_config['name']
        else:
            # 兼容单账号模式
            self.token = GITHUB_TOKEN
            self.username = GITHUB_USERNAME
            self.email = GITHUB_EMAIL
            self.repo_name = GITHUB_REPO
            self.account_name = 'default'
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'{self.username}-auto-commit'
        })
        self.repo_url = f'{GITHUB_API_BASE}/repos/{self.username}/{self.repo_name}'
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """发送HTTP请求，带重试机制"""
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.request(
                    method, url, timeout=REQUEST_TIMEOUT, **kwargs
                )
                if response.status_code < 500:  # 不重试客户端错误
                    return response
            except requests.RequestException as e:
                logger.warning(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)  # 指数退避
        
        raise requests.RequestException(f"请求失败，已重试 {MAX_RETRIES} 次")
    
    def check_repo_exists(self) -> bool:
        """检查仓库是否存在"""
        try:
            response = self._make_request('GET', self.repo_url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"检查仓库失败: {e}")
            return False
    
    def create_repo(self) -> bool:
        """创建仓库"""
        try:
            data = {
                'name': GITHUB_REPO,
                'description': '自动提交仓库 - 保持GitHub贡献图活跃',
                'private': False,
                'auto_init': True
            }
            response = self._make_request(
                'POST', f'{GITHUB_API_BASE}/user/repos', json=data
            )
            
            if response.status_code == 201:
                logger.info(f"✅ 仓库 {GITHUB_REPO} 创建成功")
                return True
            else:
                logger.error(f"❌ 创建仓库失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"创建仓库异常: {e}")
            return False
    
    def get_latest_commit_sha(self, branch: str = MAIN_BRANCH) -> Optional[str]:
        """获取最新提交的SHA"""
        try:
            url = f'{self.repo_url}/git/refs/heads/{branch}'
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                return response.json()['object']['sha']
            return None
        except Exception as e:
            logger.error(f"获取提交SHA失败: {e}")
            return None
    
    def create_blob(self, content: str) -> Optional[str]:
        """创建blob对象"""
        try:
            data = {
                'content': base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                'encoding': 'base64'
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/git/blobs', json=data
            )
            
            if response.status_code == 201:
                return response.json()['sha']
            return None
        except Exception as e:
            logger.error(f"创建blob失败: {e}")
            return None
    
    def create_tree(self, base_tree_sha: str, file_path: str, blob_sha: str) -> Optional[str]:
        """创建tree对象"""
        try:
            data = {
                'base_tree': base_tree_sha,
                'tree': [{
                    'path': file_path,
                    'mode': '100644',
                    'type': 'blob',
                    'sha': blob_sha
                }]
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/git/trees', json=data
            )
            
            if response.status_code == 201:
                return response.json()['sha']
            return None
        except Exception as e:
            logger.error(f"创建tree失败: {e}")
            return None
    
    def create_commit(self, tree_sha: str, parent_sha: str, message: str) -> Optional[str]:
        """创建提交"""
        try:
            data = {
                'message': message,
                'tree': tree_sha,
                'parents': [parent_sha],
                'author': {
                    'name': GITHUB_USERNAME,
                    'email': GITHUB_EMAIL,
                    'date': datetime.utcnow().isoformat() + 'Z'
                },
                'committer': {
                    'name': GITHUB_USERNAME,
                    'email': GITHUB_EMAIL,
                    'date': datetime.utcnow().isoformat() + 'Z'
                }
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/git/commits', json=data
            )
            
            if response.status_code == 201:
                return response.json()['sha']
            return None
        except Exception as e:
            logger.error(f"创建提交失败: {e}")
            return None
    
    def update_reference(self, branch: str, commit_sha: str) -> bool:
        """更新分支引用"""
        try:
            data = {'sha': commit_sha}
            response = self._make_request(
                'PATCH', f'{self.repo_url}/git/refs/heads/{branch}', json=data
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"更新引用失败: {e}")
            return False
    
    def create_branch(self, branch_name: str, base_sha: str) -> bool:
        """创建新分支"""
        try:
            data = {
                'ref': f'refs/heads/{branch_name}',
                'sha': base_sha
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/git/refs', json=data
            )
            return response.status_code == 201
        except Exception as e:
            logger.error(f"创建分支失败: {e}")
            return False
    
    def create_pull_request(self, branch_name: str, title: str, body: str) -> Optional[str]:
        """创建Pull Request"""
        try:
            data = {
                'title': title,
                'body': body,
                'head': branch_name,
                'base': MAIN_BRANCH
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/pulls', json=data
            )
            
            if response.status_code == 201:
                return response.json()['html_url']
            return None
        except Exception as e:
            logger.error(f"创建PR失败: {e}")
            return None
    
    def generate_daily_content(self) -> str:
        """生成每日内容"""
        now = datetime.now()
        
        # 生成随机内容
        activities = [
            "学习新技术", "代码重构", "性能优化", "文档更新", "测试用例",
            "Bug修复", "功能开发", "代码审查", "架构设计", "技术调研"
        ]
        
        technologies = [
            "Python", "JavaScript", "Go", "Rust", "TypeScript",
            "React", "Vue", "Docker", "Kubernetes", "Redis"
        ]
        
        activity = random.choice(activities)
        tech = random.choice(technologies)
        
        content = f"""# 每日提交记录

## 📅 {now.strftime('%Y-%m-%d')}

### 🎯 今日活动
- **主要活动**: {activity}
- **技术栈**: {tech}
- **提交时间**: {now.strftime('%H:%M:%S')}

### 📊 统计信息
- 总提交次数: {random.randint(100, 999)}
- 代码行数: {random.randint(1000, 9999)}
- 活跃天数: {(now - datetime(2024, 1, 1)).days}

### 💭 今日感悟
{random.choice([
    '代码如诗，每一行都是艺术的体现。',
    '持续学习，永不止步。',
    '优雅的代码是最好的文档。',
    '简单是复杂的终极形式。',
    '代码质量比数量更重要。'
])}

---
*自动生成于 {now.isoformat()}*
"""
        return content
    
    def auto_commit_and_pr(self) -> Tuple[bool, str]:
        """执行自动提交和PR创建"""
        account_logger = setup_logging(self.account_name)
        try:
            # 检查仓库是否存在
            if not self.check_repo_exists():
                account_logger.info(f"[{self.account_name}] 仓库不存在，正在创建...")
                if not self.create_repo():
                    return False, "创建仓库失败"
                time.sleep(5)  # 等待仓库创建完成
            
            # 获取最新提交
            latest_sha = self.get_latest_commit_sha()
            if not latest_sha:
                return False, "获取最新提交失败"
            
            # 生成内容
            now = datetime.now()
            content = self.generate_daily_content()
            file_path = f"daily_commits/{now.strftime('%Y/%m')}/{now.strftime('%Y-%m-%d')}.md"
            
            # 创建blob
            blob_sha = self.create_blob(content)
            if not blob_sha:
                return False, "创建blob失败"
            
            # 获取基础tree
            response = self._make_request('GET', f'{self.repo_url}/git/commits/{latest_sha}')
            if response.status_code != 200:
                return False, "获取基础tree失败"
            
            base_tree_sha = response.json()['tree']['sha']
            
            # 创建tree
            tree_sha = self.create_tree(base_tree_sha, file_path, blob_sha)
            if not tree_sha:
                return False, "创建tree失败"
            
            # 创建提交消息
            commit_message = COMMIT_MESSAGE_TEMPLATE.format(
                date=now.strftime('%Y-%m-%d')
            )
            
            # 创建提交
            commit_sha = self.create_commit(tree_sha, latest_sha, commit_message)
            if not commit_sha:
                return False, "创建提交失败"
            
            # 创建分支
            branch_name = f"{PR_BRANCH_PREFIX}{now.strftime('%Y%m%d-%H%M%S')}"
            if not self.create_branch(branch_name, commit_sha):
                return False, "创建分支失败"
            
            # 创建PR
            pr_title = PR_TITLE_TEMPLATE.format(date=now.strftime('%Y-%m-%d'))
            pr_body = PR_BODY_TEMPLATE.format(
                date=now.strftime('%Y-%m-%d'),
                time=now.strftime('%H:%M:%S')
            )
            
            pr_url = self.create_pull_request(branch_name, pr_title, pr_body)
            if not pr_url:
                return False, "创建PR失败"
            
            account_logger.info(f"[{self.account_name}] ✅ 自动提交成功！")
            account_logger.info(f"[{self.account_name}] 📁 文件: {file_path}")
            account_logger.info(f"[{self.account_name}] 🔗 PR链接: {pr_url}")
            
            return True, pr_url
            
        except Exception as e:
            account_logger.error(f"[{self.account_name}] 自动提交异常: {e}")
            return False, str(e)

def run_multi_account_commits(accounts: List[Dict[str, str]]) -> Dict[str, Tuple[bool, str]]:
    """多账号并发提交"""
    results = {}
    
    def commit_for_account(account_config):
        auto_commit = GitHubAutoCommit(account_config)
        return account_config['name'], auto_commit.auto_commit_and_pr()
    
    with ThreadPoolExecutor(max_workers=min(len(accounts), 5)) as executor:
        future_to_account = {executor.submit(commit_for_account, account): account for account in accounts}
        
        for future in as_completed(future_to_account):
            account_name, result = future.result()
            results[account_name] = result
    
    return results

def main():
    """主函数"""
    try:
        # 验证配置
        validate_config()
        logger.info("🚀 开始执行自动提交任务")
        
        # 检查是否有多账号配置
        if hasattr(globals(), 'GITHUB_ACCOUNTS') and GITHUB_ACCOUNTS:
            # 多账号模式
            logger.info(f"检测到 {len(GITHUB_ACCOUNTS)} 个账号，开始并发提交")
            results = run_multi_account_commits(GITHUB_ACCOUNTS)
            
            for account_name, (success, result) in results.items():
                if success:
                    logger.info(f"🎉 [{account_name}] 任务完成！PR链接: {result}")
                else:
                    logger.error(f"❌ [{account_name}] 任务失败: {result}")
        else:
            # 单账号模式
            auto_commit = GitHubAutoCommit()
            success, result = auto_commit.auto_commit_and_pr()
            
            if success:
                logger.info(f"🎉 任务完成！PR链接: {result}")
            else:
                logger.error(f"❌ 任务失败: {result}")
                
    except Exception as e:
        logger.error(f"程序异常: {e}")

if __name__ == '__main__':
    main()