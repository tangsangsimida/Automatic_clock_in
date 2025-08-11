#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统测试脚本
用于验证GitHub自动提交系统的各个组件是否正常工作
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemTester:
    """系统测试类"""
    
    def __init__(self):
        self.test_results = []
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
    
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {test_name}: {message}")
    
    def test_python_version(self) -> bool:
        """测试Python版本"""
        try:
            version = sys.version_info
            if version.major >= 3 and version.minor >= 6:
                self.log_test_result(
                    "Python版本检查", 
                    True, 
                    f"Python {version.major}.{version.minor}.{version.micro}"
                )
                return True
            else:
                self.log_test_result(
                    "Python版本检查", 
                    False, 
                    f"需要Python 3.6+，当前版本: {version.major}.{version.minor}.{version.micro}"
                )
                return False
        except Exception as e:
            self.log_test_result("Python版本检查", False, str(e))
            return False
    
    def test_required_modules(self) -> bool:
        """测试必需的Python模块"""
        required_modules = [
            'requests',
            'schedule',
            'json',
            'datetime',
            'logging',
            'threading',
            'signal',
            'base64',
            'hashlib',
            'random'
        ]
        
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                missing_modules.append(module)
        
        if not missing_modules:
            self.log_test_result(
                "Python模块检查", 
                True, 
                "所有必需模块都已安装"
            )
            return True
        else:
            self.log_test_result(
                "Python模块检查", 
                False, 
                f"缺少模块: {', '.join(missing_modules)}"
            )
            return False
    
    def test_file_structure(self) -> bool:
        """测试文件结构"""
        required_files = [
            'config.py',
            'auto_commit.py',
            'scheduler.py',
            'requirements.txt',
            'install.sh',
            'run.sh'
        ]
        
        missing_files = []
        
        for file in required_files:
            file_path = os.path.join(self.script_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if not missing_files:
            self.log_test_result(
                "文件结构检查", 
                True, 
                "所有必需文件都存在"
            )
            return True
        else:
            self.log_test_result(
                "文件结构检查", 
                False, 
                f"缺少文件: {', '.join(missing_files)}"
            )
            return False
    
    def test_config_file(self) -> bool:
        """测试配置文件"""
        try:
            # 尝试导入配置
            sys.path.insert(0, self.script_dir)
            from config import validate_config, load_accounts_config
            
            # 验证基本配置
            validate_config()
            
            # 测试账号配置加载
            accounts = load_accounts_config()
            
            self.log_test_result(
                "配置文件检查", 
                True, 
                f"配置文件验证通过，成功加载 {len(accounts)} 个账号配置"
            )
            
            # 显示账号详情
            for account in accounts:
                print(f"  - {account['name']}: {account['username']} ({account['commit_frequency']})")
            
            return True
            
        except Exception as e:
            self.log_test_result(
                "配置文件检查", 
                False, 
                f"配置验证失败: {str(e)}"
            )
            return False
    
    def test_github_connectivity(self) -> bool:
        """测试GitHub连接"""
        try:
            import requests
            
            # 测试GitHub API连接
            response = requests.get('https://api.github.com', timeout=10)
            
            if response.status_code == 200:
                self.log_test_result(
                    "GitHub连接测试", 
                    True, 
                    "GitHub API连接正常"
                )
                return True
            else:
                self.log_test_result(
                    "GitHub连接测试", 
                    False, 
                    f"GitHub API响应异常: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "GitHub连接测试", 
                False, 
                f"连接失败: {str(e)}"
            )
            return False
    
    def test_github_auth(self) -> bool:
        """测试GitHub认证"""
        try:
            # 导入配置模块
            sys.path.insert(0, self.script_dir)
            from config import load_accounts_config
            import requests
            
            accounts = load_accounts_config()
            success_count = 0
            enabled_count = 0
            
            for account in accounts:
                if not account.get('enabled', True):
                    continue
                    
                enabled_count += 1
                
                headers = {
                    'Authorization': f'token {account["token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    # 验证用户名匹配
                    if user_data.get('login') == account['username']:
                        success_count += 1
                    else:
                        self.log_test_result(
                            f"GitHub认证测试 - {account['name']}", 
                            False, 
                            f"用户名不匹配: 配置={account['username']}, 实际={user_data.get('login')}"
                        )
                        continue
                else:
                    self.log_test_result(
                        f"GitHub认证测试 - {account['name']}", 
                        False, 
                        f"认证失败: {response.status_code}"
                    )
                    continue
            
            if success_count == enabled_count and enabled_count > 0:
                self.log_test_result(
                    "GitHub认证测试", 
                    True, 
                    f"所有账号认证成功 ({success_count}/{enabled_count})"
                )
                return True
            else:
                self.log_test_result(
                    "GitHub认证测试", 
                    False, 
                    f"部分账号认证失败 ({success_count}/{enabled_count})"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                "GitHub认证测试", 
                False, 
                f"认证测试异常: {str(e)}"
            )
            return False
    
    def test_directory_permissions(self) -> bool:
        """测试目录权限"""
        try:
            # 测试创建目录
            test_dirs = ['data', 'logs']
            
            for dir_name in test_dirs:
                dir_path = os.path.join(self.script_dir, dir_name)
                
                # 尝试创建目录
                os.makedirs(dir_path, exist_ok=True)
                
                # 测试写入权限
                test_file = os.path.join(dir_path, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                
                # 清理测试文件
                os.remove(test_file)
            
            self.log_test_result(
                "目录权限测试", 
                True, 
                "目录创建和写入权限正常"
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "目录权限测试", 
                False, 
                f"权限测试失败: {str(e)}"
            )
            return False
    
    def test_script_execution(self) -> bool:
        """测试脚本执行权限"""
        try:
            scripts = ['install.sh', 'run.sh']
            
            for script in scripts:
                script_path = os.path.join(self.script_dir, script)
                if os.path.exists(script_path):
                    # 检查是否有执行权限
                    if not os.access(script_path, os.X_OK):
                        # 尝试添加执行权限
                        os.chmod(script_path, 0o755)
            
            self.log_test_result(
                "脚本执行权限测试", 
                True, 
                "脚本执行权限正常"
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                "脚本执行权限测试", 
                False, 
                f"权限设置失败: {str(e)}"
            )
            return False
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        logger.info("🚀 开始系统测试...")
        logger.info("=" * 50)
        
        tests = [
            self.test_python_version,
            self.test_required_modules,
            self.test_file_structure,
            self.test_directory_permissions,
            self.test_script_execution,
            self.test_config_file,
            self.test_github_connectivity,
            self.test_github_auth
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                logger.error(f"测试异常: {e}")
        
        logger.info("=" * 50)
        logger.info(f"📊 测试完成: {passed}/{total} 通过")
        
        if passed == total:
            logger.info("🎉 所有测试通过！系统准备就绪。")
        else:
            logger.warning(f"⚠️  有 {total - passed} 个测试失败，请检查上述错误信息。")
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': passed / total * 100,
            'results': self.test_results
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """生成测试报告"""
        if not output_file:
            output_file = os.path.join(self.script_dir, 'test_report.json')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'platform': sys.platform,
                'script_directory': self.script_dir
            },
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['success']]),
                'failed': len([r for r in self.test_results if not r['success']])
            },
            'test_results': self.test_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 测试报告已保存到: {output_file}")
        return output_file

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub自动提交系统测试工具')
    parser.add_argument('--report', '-r', help='生成测试报告文件路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--account', '-a', help='测试指定账号')
    parser.add_argument('--quick', '-q', action='store_true', help='快速测试（跳过GitHub连接测试）')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 如果指定了账号，只测试该账号
    if args.account:
        logger.info(f"🎯 测试指定账号: {args.account}")
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from config import get_account_by_name
            import requests
            
            account = get_account_by_name(args.account)
            logger.info(f"✅ 找到账号配置: {account['name']}")
            
            # 测试单个账号的GitHub连接
            if not args.quick:
                headers = {
                    'Authorization': f'token {account["token"]}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                if response.status_code == 200:
                    user_info = response.json()
                    logger.info(f"✅ GitHub连接成功: {user_info.get('login')}")
                else:
                    logger.error(f"❌ GitHub连接失败: {response.status_code}")
                    sys.exit(1)
            
            logger.info(f"🎉 账号 {args.account} 测试通过！")
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"❌ 账号测试失败: {e}")
            sys.exit(1)
    
    # 创建测试器并运行测试
    tester = SystemTester()
    results = tester.run_all_tests()
    
    # 生成报告
    if args.report or results['failed'] > 0:
        tester.generate_report(args.report)
    
    # 返回适当的退出码
    sys.exit(0 if results['failed'] == 0 else 1)

if __name__ == '__main__':
    main()