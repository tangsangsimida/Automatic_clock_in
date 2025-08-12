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
    
    def __init__(self, account_config: Dict[str, str]):
        if not account_config:
            raise ValueError("account_config is required")
            
        self.config = account_config  # 保存完整配置
        self.token = account_config['token']
        self.username = account_config['username']
        self.email = account_config['email']
        self.repo_name = account_config['repo']
        self.account_name = account_config['name']
            
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': f'{self.username}-auto-commit'
        })
        self.repo_url = f'{GITHUB_API_BASE}/repos/{self.username}/{self.repo_name}'
        logger.info(f"仓库URL: {self.repo_url}")
        logger.info(f"用户名: {self.username}, 仓库名: {self.repo_name}")
    
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
            if response.status_code == 200:
                logger.info(f"仓库 {self.repo_name} 已存在")
                return True
            elif response.status_code == 404:
                logger.info(f"仓库 {self.repo_name} 不存在")
                return False
            else:
                logger.warning(f"检查仓库状态异常: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"检查仓库失败: {e}")
            return False
    
    def create_repo(self) -> bool:
        """创建仓库"""
        try:
            data = {
                'name': self.repo_name,
                'description': '自动提交仓库 - 保持GitHub贡献图活跃',
                'private': False,
                'auto_init': True
            }
            logger.info(f"正在创建仓库，请求数据: {data}")
            response = self._make_request(
                'POST', f'{GITHUB_API_BASE}/user/repos', json=data
            )
            
            logger.info(f"创建仓库响应状态码: {response.status_code}")
            logger.info(f"创建仓库响应内容: {response.text}")
            
            if response.status_code == 201:
                logger.info(f"✅ 仓库 {self.repo_name} 创建成功")
                # 等待一段时间让仓库完全创建
                time.sleep(2)
                return True
            elif response.status_code == 422:
                # 仓库已存在，检查是否确实存在
                response_data = response.json()
                error_message = response_data.get('message', '')
                errors = response_data.get('errors', [])
                
                logger.info(f"收到422错误，错误信息: {error_message}")
                logger.info(f"错误详情: {errors}")
                
                # 检查是否是仓库名已存在的错误
                name_exists = False
                if 'name already exists' in error_message:
                    name_exists = True
                else:
                    for error in errors:
                        if error.get('field') == 'name' and 'already exists' in error.get('message', ''):
                            name_exists = True
                            break
                
                if name_exists:
                    logger.info(f"仓库 {self.repo_name} 已存在，跳过创建")
                    # 验证仓库确实存在
                    if self.check_repo_exists():
                        logger.info(f"验证确认仓库 {self.repo_name} 存在")
                        return True
                    else:
                        logger.error(f"仓库 {self.repo_name} 声称已存在但验证失败")
                        return False
                else:
                    logger.error(f"❌ 创建仓库失败: {response.text}")
                    return False
            else:
                logger.error(f"❌ 创建仓库失败，状态码: {response.status_code}, 响应: {response.text}")
                return False
        except Exception as e:
            logger.error(f"创建仓库异常: {e}")
            return False
    
    def get_latest_commit_sha(self, branch: str = MAIN_BRANCH) -> Optional[str]:
        """获取最新提交的SHA"""
        try:
            # 先尝试指定的分支
            url = f'{self.repo_url}/git/refs/heads/{branch}'
            response = self._make_request('GET', url)
            
            if response.status_code == 200:
                logger.info(f"成功获取{branch}分支的最新提交")
                return response.json()['object']['sha']
            elif response.status_code == 404:
                logger.info(f"{branch}分支不存在，尝试其他分支")
            else:
                logger.warning(f"获取{branch}分支失败: {response.status_code} - {response.text}")
            
            # 如果指定分支不存在，尝试其他常见的默认分支
            if branch == 'main':
                # 尝试master分支
                url = f'{self.repo_url}/git/refs/heads/master'
                response = self._make_request('GET', url)
                if response.status_code == 200:
                    logger.info("使用master分支作为默认分支")
                    return response.json()['object']['sha']
                elif response.status_code == 404:
                    logger.info("master分支也不存在")
                else:
                    logger.warning(f"获取master分支失败: {response.status_code} - {response.text}")
            elif branch == 'master':
                # 尝试main分支
                url = f'{self.repo_url}/git/refs/heads/main'
                response = self._make_request('GET', url)
                if response.status_code == 200:
                    logger.info("使用main分支作为默认分支")
                    return response.json()['object']['sha']
                elif response.status_code == 404:
                    logger.info("main分支也不存在")
                else:
                    logger.warning(f"获取main分支失败: {response.status_code} - {response.text}")
            
            # 如果都没有找到，可能是空仓库
            logger.info("仓库可能是空的，没有任何提交")
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
                logger.info("成功创建blob对象")
                return response.json()['sha']
            else:
                logger.error(f"创建blob失败: {response.status_code} - {response.text}")
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
    
    def create_commit(self, tree_sha: str, parent_sha: Optional[str], message: str) -> Optional[str]:
        """创建提交"""
        try:
            data = {
                'message': message,
                'tree': tree_sha,
                'parents': [] if parent_sha is None else [parent_sha],
                'author': {
                    'name': self.username,
                    'email': self.email,
                    'date': datetime.utcnow().isoformat() + 'Z'
                },
                'committer': {
                    'name': self.username,
                    'email': self.email,
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
    
    def create_reference(self, branch: str, commit_sha: str) -> bool:
        """创建分支引用"""
        try:
            data = {
                'ref': f'refs/heads/{branch}',
                'sha': commit_sha
            }
            response = self._make_request(
                'POST', f'{self.repo_url}/git/refs', json=data
            )
            if response.status_code == 201:
                logger.info(f"成功创建{branch}分支")
                return True
            else:
                logger.error(f"创建分支失败: {response.text}")
                return False
        except Exception as e:
            logger.error(f"创建引用失败: {e}")
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
    
    def create_pull_request(self, branch_name: str, title: str, body: str) -> Optional[Tuple[str, int]]:
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
                pr_data = response.json()
                return pr_data['html_url'], pr_data['number']
            return None
        except Exception as e:
            logger.error(f"创建PR失败: {e}")
            return None
    
    def merge_pull_request(self, pr_number: int, commit_title: str = None) -> bool:
        """合并Pull Request"""
        try:
            # 首先检查PR状态
            pr_response = self._make_request(
                'GET', f'{self.repo_url}/pulls/{pr_number}'
            )
            
            if pr_response.status_code != 200:
                logger.error(f"[{self.account_name}] 获取PR状态失败: {pr_response.status_code} - {pr_response.text}")
                return False
            
            pr_data = pr_response.json()
            pr_state = pr_data.get('state')
            mergeable = pr_data.get('mergeable')
            merged = pr_data.get('merged')
            
            logger.info(f"[{self.account_name}] PR状态: state={pr_state}, mergeable={mergeable}, merged={merged}")
            
            if merged:
                logger.info(f"[{self.account_name}] PR已经被合并")
                return True
            
            if pr_state != 'open':
                logger.error(f"[{self.account_name}] PR状态不是open: {pr_state}")
                return False
            
            if mergeable is False:
                logger.error(f"[{self.account_name}] PR不可合并，可能存在冲突")
                return False
            
            # 检查用户权限
            repo_response = self._make_request(
                'GET', f'{self.repo_url}'
            )
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                permissions = repo_data.get('permissions', {})
                can_push = permissions.get('push', False)
                can_admin = permissions.get('admin', False)
                logger.info(f"[{self.account_name}] 仓库权限: push={can_push}, admin={can_admin}")
                
                if not (can_push or can_admin):
                    logger.error(f"[{self.account_name}] 用户没有合并PR的权限")
                    return False
            else:
                logger.warning(f"[{self.account_name}] 无法获取仓库权限信息: {repo_response.status_code}")
            
            # 检查分支保护规则
            branch_protection_response = self._make_request(
                'GET', f'{self.repo_url}/branches/{MAIN_BRANCH}/protection'
            )
            if branch_protection_response.status_code == 200:
                protection_data = branch_protection_response.json()
                required_reviews = protection_data.get('required_pull_request_reviews', {})
                min_reviews = required_reviews.get('required_approving_review_count', 0)
                dismiss_stale = required_reviews.get('dismiss_stale_reviews', False)
                require_code_owner = required_reviews.get('require_code_owner_reviews', False)
                
                logger.info(f"[{self.account_name}] 分支保护: 需要{min_reviews}个审核, dismiss_stale={dismiss_stale}, require_code_owner={require_code_owner}")
                
                if min_reviews > 0:
                    # 检查PR的审核状态
                    reviews_response = self._make_request(
                        'GET', f'{self.repo_url}/pulls/{pr_number}/reviews'
                    )
                    if reviews_response.status_code == 200:
                        reviews = reviews_response.json()
                        approved_count = sum(1 for review in reviews if review.get('state') == 'APPROVED')
                        logger.info(f"[{self.account_name}] PR已获得{approved_count}个审核批准，需要{min_reviews}个")
                        
                        if approved_count < min_reviews:
                            logger.error(f"[{self.account_name}] PR审核不足，无法合并")
                            return False
            elif branch_protection_response.status_code == 404:
                logger.info(f"[{self.account_name}] 分支无保护规则")
            else:
                logger.warning(f"[{self.account_name}] 无法获取分支保护信息: {branch_protection_response.status_code}")
            
            # 尝试合并PR
            data = {
                'commit_title': commit_title or f'Merge PR #{pr_number}',
                'merge_method': 'merge'  # 可选: merge, squash, rebase
            }
            
            # 如果用户是仓库所有者且有管理员权限，尝试绕过保护规则
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                owner_login = repo_data.get('owner', {}).get('login', '')
                permissions = repo_data.get('permissions', {})
                is_admin = permissions.get('admin', False)
                
                if self.username == owner_login and is_admin:
                    logger.info(f"[{self.account_name}] 用户是仓库所有者，尝试管理员合并")
                    # 对于仓库所有者，可以尝试强制合并
                    data['merge_method'] = 'squash'  # 使用squash合并可能更容易成功
            
            # 尝试合并，如果因为分支冲突失败则重试
            max_retries = 5
            base_wait_time = 1.0
            
            for attempt in range(max_retries):
                # 在重试前添加随机延迟，避免多个账户同时操作
                if attempt > 0:
                    wait_time = base_wait_time * (2 ** attempt) + random.uniform(0.5, 1.5)
                    logger.info(f"[{self.account_name}] 等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                
                response = self._make_request(
                    'PUT', f'{self.repo_url}/pulls/{pr_number}/merge', json=data
                )
                
                if response.status_code == 200:
                    logger.info(f"[{self.account_name}] PR合并成功")
                    return True
                
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass
                
                # 检查是否是因为分支被修改导致的冲突
                if response.status_code == 405 and ("Base branch was modified" in error_msg or "merge conflict" in error_msg.lower()):
                    logger.warning(f"[{self.account_name}] 检测到分支冲突: {error_msg} (尝试 {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:  # 不是最后一次尝试
                        # 重新检查PR状态
                        pr_response = self._make_request(
                            'GET', f'{self.repo_url}/pulls/{pr_number}'
                        )
                        
                        if pr_response.status_code == 200:
                            pr_data = pr_response.json()
                            if pr_data.get('merged'):
                                logger.info(f"[{self.account_name}] PR已被其他操作合并")
                                return True
                            
                            # 检查是否仍然可以合并
                            mergeable = pr_data.get('mergeable')
                            if mergeable is False:
                                logger.error(f"[{self.account_name}] PR存在真实冲突，无法自动合并")
                                return False
                            elif mergeable is None:
                                logger.info(f"[{self.account_name}] PR合并状态检查中，继续重试")
                        
                        continue  # 重试
                    else:
                        logger.error(f"[{self.account_name}] 分支冲突重试次数已用完")
                        return False
                
                # 检查是否是权限问题
                elif response.status_code == 403:
                    logger.error(f"[{self.account_name}] 权限不足，无法合并PR: {error_msg}")
                    return False
                
                # 检查是否是PR已经合并
                elif response.status_code == 405 and "Pull Request is not mergeable" in error_msg:
                    # 再次检查PR状态
                    pr_response = self._make_request(
                        'GET', f'{self.repo_url}/pulls/{pr_number}'
                    )
                    if pr_response.status_code == 200:
                        pr_data = pr_response.json()
                        if pr_data.get('merged'):
                            logger.info(f"[{self.account_name}] PR已被合并")
                            return True
                    
                    logger.error(f"[{self.account_name}] PR不可合并: {error_msg}")
                    return False
                
                # 其他类型的错误，记录并返回
                else:
                    logger.error(f"[{self.account_name}] PR合并失败: {response.status_code} - {error_msg}")
                    return False
            
            # 所有重试都失败了
            logger.error(f"[{self.account_name}] PR合并失败，已重试{max_retries}次")
            return False
                
        except Exception as e:
            logger.error(f"[{self.account_name}] 合并PR异常: {e}")
            return False
    
    def delete_branch(self, branch_name: str) -> bool:
        """删除分支"""
        try:
            response = self._make_request(
                'DELETE', f'{self.repo_url}/git/refs/heads/{branch_name}'
            )
            
            return response.status_code == 204
        except Exception as e:
            logger.error(f"删除分支失败: {e}")
            return False
    
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
        
        content = f"""# 每日提交记录 - {self.account_name}

## 📅 {now.strftime('%Y-%m-%d')}

### 🎯 今日活动
- **主要活动**: {activity}
- **技术栈**: {tech}
- **提交时间**: {now.strftime('%H:%M:%S')}
- **账号**: {self.account_name}

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
            is_empty_repo = latest_sha is None
            
            if is_empty_repo:
                account_logger.info(f"[{self.account_name}] 检测到空仓库，将创建初始提交")
            
            # 生成内容
            now = datetime.now()
            content = self.generate_daily_content()
            # 将文件放到用户专属文件夹中，避免合并冲突
            file_path = f"users/{self.account_name}/daily_commits/{now.strftime('%Y/%m')}/{now.strftime('%Y-%m-%d')}.md"
            
            # 创建blob
            blob_sha = self.create_blob(content)
            if not blob_sha:
                return False, "创建blob失败"
            
            # 获取基础tree
            base_tree_sha = None
            if not is_empty_repo:
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
            parent_sha = None if is_empty_repo else latest_sha
            commit_sha = self.create_commit(tree_sha, parent_sha, commit_message)
            if not commit_sha:
                return False, "创建提交失败"
            
            if is_empty_repo:
                # 空仓库：直接创建main分支
                if not self.create_reference('main', commit_sha):
                    return False, "创建main分支失败"
                
                account_logger.info(f"[{self.account_name}] ✅ 初始提交成功！")
                account_logger.info(f"[{self.account_name}] 📁 文件: {file_path}")
                account_logger.info(f"[{self.account_name}] 🌟 已建立仓库初始状态")
                
                return True, "初始提交完成"
            else:
                # 非空仓库：创建分支和PR
                branch_name = f"{PR_BRANCH_PREFIX}{self.account_name}-{now.strftime('%Y%m%d-%H%M%S')}"
                if not self.create_branch(branch_name, commit_sha):
                    return False, "创建分支失败"
                
                # 创建PR
                pr_title = PR_TITLE_TEMPLATE.format(date=now.strftime('%Y-%m-%d'))
                pr_body = PR_BODY_TEMPLATE.format(
                    date=now.strftime('%Y-%m-%d'),
                    time=now.strftime('%H:%M:%S')
                )
                
                pr_result = self.create_pull_request(branch_name, pr_title, pr_body)
                if not pr_result:
                    return False, "创建PR失败"
                
                pr_url, pr_number = pr_result
                account_logger.info(f"[{self.account_name}] ✅ PR创建成功！")
                account_logger.info(f"[{self.account_name}] 📁 文件: {file_path}")
                account_logger.info(f"[{self.account_name}] 🔗 PR链接: {pr_url}")
                
                # 检查是否启用自动合并
                auto_merge = self.config.get('auto_merge', True)
                delete_branch_after_merge = self.config.get('delete_branch_after_merge', True)
                
                if auto_merge:
                    # 等待一小段时间确保PR创建完成
                    time.sleep(2)
                    
                    # 自动合并PR
                    merge_title = f"Auto merge: {pr_title}"
                    if self.merge_pull_request(pr_number, merge_title):
                        account_logger.info(f"[{self.account_name}] ✅ PR自动合并成功！")
                        
                        # 根据配置决定是否删除分支
                        if delete_branch_after_merge:
                            time.sleep(2)
                            if self.delete_branch(branch_name):
                                account_logger.info(f"[{self.account_name}] ✅ 分支 {branch_name} 已删除")
                                return True, f"PR已自动合并并删除分支: {pr_url}"
                            else:
                                account_logger.warning(f"[{self.account_name}] ⚠️ 删除分支 {branch_name} 失败")
                                return True, f"PR已自动合并但删除分支失败: {pr_url}"
                        else:
                            return True, f"PR已自动合并: {pr_url}"
                    else:
                        account_logger.error(f"[{self.account_name}] ❌ PR自动合并失败")
                        return False, f"PR创建成功但合并失败: {pr_url}"
                else:
                    account_logger.info(f"[{self.account_name}] ✅ PR创建成功，等待手动合并")
                    return True, f"PR创建成功，等待手动合并: {pr_url}"
            
        except Exception as e:
            account_logger.error(f"[{self.account_name}] 自动提交异常: {e}")
            return False, str(e)

def run_multi_account_commits(accounts: List[Dict[str, str]]) -> Dict[str, Tuple[bool, str]]:
    """多账号并发提交"""
    results = {}
    
    def commit_for_account(account_config, delay=0):
        # 添加随机延迟避免竞争条件
        if delay > 0:
            time.sleep(delay)
        auto_commit = GitHubAutoCommit(account_config)
        return account_config['name'], auto_commit.auto_commit_and_pr()
    
    with ThreadPoolExecutor(max_workers=min(len(accounts), 5)) as executor:
        # 为每个账户分配不同的延迟时间
        future_to_account = {}
        for i, account in enumerate(accounts):
            delay = i * 0.5  # 每个账户延迟0.5秒
            future_to_account[executor.submit(commit_for_account, account, delay)] = account
        
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