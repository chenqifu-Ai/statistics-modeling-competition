#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据收集进度跟踪工具
用于记录和追踪统计数据收集进度
"""

import os
import json
from datetime import datetime

class DataCollectionTracker:
    """数据收集进度跟踪器"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.progress_file = os.path.join(base_dir, 'data', 'collection_progress.json')
        self.log_file = os.path.join(base_dir, 'data', 'collection_log.txt')
        self._init_files()
    
    def _init_files(self):
        """初始化进度文件"""
        if not os.path.exists(self.progress_file):
            initial_data = {
                'created_at': datetime.now().isoformat(),
                'data_sources': {
                    '国家统计局': {
                        'status': '未开始',
                        'priority': 1,
                        'url': 'http://www.stats.gov.cn/',
                        'target_data': ['统计年鉴', '卫生健康统计'],
                        'years': '2011-2024',
                        'collected_files': [],
                        'last_updated': None
                    },
                    '国家卫健委': {
                        'status': '未开始',
                        'priority': 2,
                        'url': 'http://www.nhc.gov.cn/',
                        'target_data': ['卫生健康统计年鉴', '中医医院运营'],
                        'years': '2011-2024',
                        'collected_files': [],
                        'last_updated': None
                    },
                    '中医药管理局': {
                        'status': '未开始',
                        'priority': 3,
                        'url': 'http://www.satcm.gov.cn/',
                        'target_data': ['中医药事业发展报告', '专项统计'],
                        'years': '2011-2024',
                        'collected_files': [],
                        'last_updated': None
                    },
                    '国家医保局': {
                        'status': '未开始',
                        'priority': 4,
                        'url': 'http://www.nhsa.gov.cn/',
                        'target_data': ['医保基金运行报告', '中医药医保数据'],
                        'years': '2011-2024',
                        'collected_files': [],
                        'last_updated': None
                    }
                },
                'total_progress': {
                    'total_sources': 4,
                    'completed': 0,
                    'in_progress': 0,
                    'not_started': 4,
                    'percentage': 0
                }
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)
    
    def update_progress(self, source_name, status, files_collected=None, notes=''):
        """更新数据收集进度"""
        with open(self.progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if source_name in data['data_sources']:
            data['data_sources'][source_name]['status'] = status
            data['data_sources'][source_name]['last_updated'] = datetime.now().isoformat()
            
            if files_collected:
                data['data_sources'][source_name]['collected_files'].extend(files_collected)
            
            # 更新总体进度
            completed = sum(1 for s in data['data_sources'].values() if s['status'] == '已完成')
            in_progress = sum(1 for s in data['data_sources'].values() if s['status'] == '进行中')
            not_started = sum(1 for s in data['data_sources'].values() if s['status'] == '未开始')
            
            data['total_progress']['completed'] = completed
            data['total_progress']['in_progress'] = in_progress
            data['total_progress']['not_started'] = not_started
            data['total_progress']['percentage'] = int((completed / data['total_progress']['total_sources']) * 100)
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 记录日志
        self._log_action(source_name, status, notes)
    
    def _log_action(self, source_name, status, notes):
        """记录操作日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {source_name} - {status}"
        if notes:
            log_entry += f" - {notes}"
        log_entry += "\n"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_progress_report(self):
        """获取进度报告"""
        with open(self.progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        report_lines = [
            "=" * 60,
            "📊 数据收集进度报告",
            "=" * 60,
            f"创建时间: {data['created_at']}",
            f"最后更新: {datetime.now().isoformat()}",
            "",
            "📈 总体进度:",
            f"  数据源总数: {data['total_progress']['total_sources']}",
            f"  已完成: {data['total_progress']['completed']}",
            f"  进行中: {data['total_progress']['in_progress']}",
            f"  未开始: {data['total_progress']['not_started']}",
            f"  完成率: {data['total_progress']['percentage']}%",
            "",
            "📋 各数据源状态:"
        ]
        
        for source_name, source_data in data['data_sources'].items():
            status_emoji = {
                '已完成': '✅',
                '进行中': '🔄',
                '未开始': '⏳'
            }.get(source_data['status'], '❓')
            
            report_lines.extend([
                f"",
                f"{status_emoji} {source_name} ({source_data['status']})",
                f"   优先级: {source_data['priority']}",
                f"   目标数据: {', '.join(source_data['target_data'])}",
                f"   年份范围: {source_data['years']}",
                f"   已收集文件: {len(source_data['collected_files'])}个"
            ])
            
            if source_data['last_updated']:
                report_lines.append(f"   最后更新: {source_data['last_updated']}")
        
        report_lines.extend([
            "",
            "=" * 60,
            "💡 下一步操作建议:",
            "1. 访问国家统计局网站下载统计年鉴",
            "2. 收集国家卫健委卫生健康统计数据",
            "3. 获取中医药管理局专项统计报告",
            "4. 整理医保基金运行数据",
            "=" * 60
        ])
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    print("="*60)
    print("📊 数据收集进度跟踪工具")
    print("="*60)
    
    # 初始化跟踪器
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    tracker = DataCollectionTracker(base_dir)
    
    # 显示当前进度
    print("\n" + tracker.get_progress_report())
    
    # 提供操作指引
    print("\n📝 使用方法:")
    print("1. 更新进度: tracker.update_progress('数据源名称', '状态', ['文件列表'], '备注')")
    print("2. 状态选项: '未开始', '进行中', '已完成'")
    print("3. 示例: tracker.update_progress('国家统计局', '进行中', notes='正在下载统计年鉴')")
    print("\n✅ 进度跟踪系统已就绪！")

if __name__ == '__main__':
    main()