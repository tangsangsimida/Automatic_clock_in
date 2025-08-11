#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器
实现每日定时执行自动提交任务
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import List
import threading
import signal
import sys

from auto_commit import GitHubAutoCommit, run_multi_account_commits
from config import (
    LOG_FILE, validate_config,
    load_accounts_config, list_enabled_accounts
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoCommitScheduler:
    """自动提交调度器"""
    
    def __init__(self):
        self.accounts = load_accounts_config()
        self.running = False
        self.thread = None
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info(f"加载了 {len(self.accounts)} 个账号配置")
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info(f"收到信号 {signum}，正在停止调度器...")
        self.stop()
        sys.exit(0)
    
    def execute_commit_task(self):
        """执行提交任务"""
        try:
            logger.info("⏰ 开始执行定时提交任务")
            
            # 获取当前时间，找出需要执行的账号
            current_time = datetime.now().strftime('%H:%M')
            accounts_to_run = []
            
            for account in self.accounts:
                if not account.get('enabled', True):
                    continue
                    
                commit_times = account.get('commit_times', [])
                if current_time in commit_times:
                    accounts_to_run.append(account)
            
            if not accounts_to_run:
                logger.info(f"当前时间 {current_time} 没有需要执行的账号")
                return
            
            logger.info(f"当前时间 {current_time}，需要执行 {len(accounts_to_run)} 个账号的提交任务")
            
            # 执行多账号提交
            results = run_multi_account_commits(accounts_to_run)
            
            # 统计结果
            success_count = sum(1 for success, _ in results.values() if success)
            total_count = len(results)
            
            logger.info(f"定时提交任务完成: {success_count}/{total_count} 成功")
            
            # 记录详细结果
            for account_name, (success, result) in results.items():
                if success:
                    logger.info(f"✅ [{account_name}] 提交成功: {result}")
                else:
                    logger.error(f"❌ [{account_name}] 提交失败: {result}")
                    
        except Exception as e:
            logger.error(f"定时任务异常: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 清除现有任务
        schedule.clear()
        
        # 收集所有账号的提交时间
        all_commit_times = set()
        
        for account in self.accounts:
            if not account.get('enabled', True):
                continue
                
            commit_times = account.get('commit_times', [])
            all_commit_times.update(commit_times)
            
            account_name = account.get('name', 'Unknown')
            logger.info(f"账号 [{account_name}] 提交时间: {commit_times}")
        
        logger.info(f"所有提交时间点: {sorted(all_commit_times)}")
        
        # 为每个时间点设置定时任务
        for commit_time in all_commit_times:
            schedule.every().day.at(commit_time).do(self.execute_commit_task)
            logger.info(f"📅 已设置定时任务: 每天 {commit_time} 执行")
        
        logger.info(f"定时任务设置完成，共 {len(all_commit_times)} 个时间点")
        
        # 添加一个测试任务（可选）
        # schedule.every(10).seconds.do(self.execute_commit_task)  # 测试用
    
    def run_scheduler(self):
        """运行调度器"""
        logger.info("🚀 调度器开始运行")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"调度器运行异常: {e}")
                time.sleep(5)
        
        logger.info("⏹️ 调度器已停止")
    
    def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("调度器已在运行中")
            return
        
        try:
            # 验证配置
            validate_config()
            
            # 设置定时任务
            self.setup_schedule()
            
            # 显示下次执行时间
            self.show_next_runs()
            
            # 启动调度器
            self.running = True
            self.thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.thread.start()
            
            logger.info("✅ 调度器启动成功")
            
        except Exception as e:
            logger.error(f"启动调度器失败: {e}")
            self.running = False
    
    def stop(self):
        """停止调度器"""
        if not self.running:
            logger.warning("调度器未在运行")
            return
        
        self.running = False
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
        
        schedule.clear()
        logger.info("🛑 调度器已停止")
    
    def show_next_runs(self):
        """显示下次执行时间"""
        jobs = schedule.get_jobs()
        if not jobs:
            logger.info("📋 没有计划的任务")
            return
        
        logger.info("📋 计划的任务:")
        for job in jobs:
            next_run = job.next_run
            if next_run:
                logger.info(f"   ⏰ {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run_once(self, account_name: str = None):
        """立即执行一次任务"""
        if account_name:
            # 执行指定账号
            try:
                account_config = next(acc for acc in self.accounts if acc['name'] == account_name)
                logger.info(f"🔄 立即执行账号 [{account_name}] 的提交任务")
                
                auto_commit = GitHubAutoCommit(account_config)
                success, result = auto_commit.auto_commit_and_pr()
                
                if success:
                    logger.info(f"✅ [{account_name}] 提交成功: {result}")
                else:
                    logger.error(f"❌ [{account_name}] 提交失败: {result}")
                    
            except StopIteration:
                logger.error(f"未找到账号: {account_name}")
            except Exception as e:
                logger.error(f"执行账号 [{account_name}] 任务异常: {e}")
        else:
            # 执行所有启用的账号
            logger.info("🔄 立即执行所有账号的提交任务")
            enabled_accounts = [acc for acc in self.accounts if acc.get('enabled', True)]
            
            if enabled_accounts:
                results = run_multi_account_commits(enabled_accounts)
                
                success_count = sum(1 for success, _ in results.values() if success)
                total_count = len(results)
                
                logger.info(f"立即执行任务完成: {success_count}/{total_count} 成功")
                
                for account_name, (success, result) in results.items():
                    if success:
                        logger.info(f"✅ [{account_name}] 提交成功: {result}")
                    else:
                        logger.error(f"❌ [{account_name}] 提交失败: {result}")
            else:
                logger.warning("没有启用的账号")
    
    def status(self):
        """获取调度器状态"""
        status_info = {
            'running': self.running,
            'jobs_count': len(schedule.get_jobs()),
            'next_runs': []
        }
        
        for job in schedule.get_jobs():
            if job.next_run:
                status_info['next_runs'].append(
                    job.next_run.strftime('%Y-%m-%d %H:%M:%S')
                )
        
        return status_info

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub自动提交调度器')
    parser.add_argument('--run-once', action='store_true', help='立即执行一次任务')
    parser.add_argument('--daemon', action='store_true', help='以守护进程模式运行')
    parser.add_argument('--status', action='store_true', help='显示调度器状态')
    
    args = parser.parse_args()
    
    scheduler = AutoCommitScheduler()
    
    try:
        if args.run_once:
            # 立即执行一次
            scheduler.run_once()
            
        elif args.status:
            # 显示状态
            status = scheduler.status()
            print(f"运行状态: {'运行中' if status['running'] else '已停止'}")
            print(f"任务数量: {status['jobs_count']}")
            if status['next_runs']:
                print("下次执行时间:")
                for next_run in status['next_runs']:
                    print(f"  {next_run}")
            
        else:
            # 启动调度器
            scheduler.start()
            
            if args.daemon:
                # 守护进程模式
                logger.info("🔄 以守护进程模式运行，按 Ctrl+C 停止")
                try:
                    while scheduler.running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("收到中断信号，正在停止...")
                finally:
                    scheduler.stop()
            else:
                # 交互模式
                logger.info("🎮 交互模式启动，输入命令:")
                logger.info("  'status' - 查看状态")
                logger.info("  'run' - 立即执行")
                logger.info("  'stop' - 停止调度器")
                logger.info("  'quit' - 退出程序")
                
                while True:
                    try:
                        cmd = input("\n> ").strip().lower()
                        
                        if cmd == 'status':
                            status = scheduler.status()
                            print(f"运行状态: {'运行中' if status['running'] else '已停止'}")
                            print(f"任务数量: {status['jobs_count']}")
                            if status['next_runs']:
                                print("下次执行时间:")
                                for next_run in status['next_runs']:
                                    print(f"  {next_run}")
                        
                        elif cmd == 'run':
                            scheduler.run_once()
                        
                        elif cmd == 'stop':
                            scheduler.stop()
                        
                        elif cmd in ['quit', 'exit', 'q']:
                            break
                        
                        elif cmd == 'help':
                            print("可用命令: status, run, stop, quit")
                        
                        else:
                            print("未知命令，输入 'help' 查看帮助")
                    
                    except (EOFError, KeyboardInterrupt):
                        break
                
                scheduler.stop()
                logger.info("👋 程序退出")
    
    except Exception as e:
        logger.error(f"程序异常: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()