#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中医药统计数据收集脚本（简化版）
用于统计建模大赛数据准备 - 不依赖外部库
"""

import os
import json
import csv
from datetime import datetime

class SimpleTCMDataCollector:
    """中医药数据收集器（简化版）"""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.data_dir = os.path.join(base_dir, 'data')
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.processed_dir = os.path.join(self.data_dir, 'processed')
        
        # 创建必要的目录
        self._create_directories()
        
        # 数据收集日志
        self.log_file = os.path.join(self.data_dir, 'collection_log.json')
        self._init_log()
    
    def _create_directories(self):
        """创建数据目录结构"""
        directories = [
            self.raw_dir,
            self.processed_dir,
            os.path.join(self.data_dir, 'analysis'),
            os.path.join(self.raw_dir, 'official'),
            os.path.join(self.raw_dir, 'survey'),
            os.path.join(self.raw_dir, 'third_party'),
            os.path.join(self.processed_dir, 'cleaned'),
            os.path.join(self.processed_dir, 'merged')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"📁 创建目录: {directory}")
    
    def _init_log(self):
        """初始化收集日志"""
        if not os.path.exists(self.log_file):
            log_data = {
                'created_at': datetime.now().isoformat(),
                'collections': [],
                'total_files': 0
            }
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def create_data_template(self):
        """创建数据模板文件"""
        headers = [
            '年份', '中医医院数量', '中医床位数量', '中医药人员数量',
            '诊疗人次', '出院人数', '床位使用率', '平均住院日',
            '医疗收入', '医保收入'
        ]
        
        template_path = os.path.join(self.raw_dir, 'official', 'tcm_hospital_template.csv')
        with open(template_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
        
        self._log_collection('内部创建', '数据模板', '完成', template_path, '创建中医医院数据收集模板')
        return template_path
    
    def create_sample_data(self):
        """创建示例数据（用于测试）"""
        years = list(range(2011, 2025))
        
        # 模拟数据
        data_rows = []
        for i, year in enumerate(years):
            row = [
                year,
                3000 + i*200,  # 中医医院数量
                50000 + i*5000,  # 中医床位数量
                400000 + i*30000,  # 中医药人员数量
                5.0 + i*0.5,  # 诊疗人次（亿人次）
                100 + i*20,  # 出院人数（万人）
                85 + i*0.5,  # 床位使用率（%）
                10 - i*0.2,  # 平均住院日（天）
                1000 + i*200,  # 医疗收入（亿元）
                600 + i*150   # 医保收入（亿元）
            ]
            data_rows.append(row)
        
        sample_path = os.path.join(self.processed_dir, 'cleaned', 'tcm_sample_data.csv')
        headers = [
            '年份', '中医医院数量', '中医床位数量', '中医药人员数量',
            '诊疗人次', '出院人数', '床位使用率', '平均住院日',
            '医疗收入', '医保收入'
        ]
        
        with open(sample_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(data_rows)
        
        self._log_collection('模拟生成', '示例数据', '完成', sample_path, '生成示例数据用于分析测试')
        return sample_path
    
    def _log_collection(self, source, data_type, status, file_path=None, notes=''):
        """记录数据收集情况"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        collection_record = {
            'timestamp': datetime.now().isoformat(),
            'source': source,
            'data_type': data_type,
            'status': status,
            'file_path': file_path,
            'notes': notes
        }
        
        log_data['collections'].append(collection_record)
        log_data['total_files'] += 1 if file_path else 0
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    
    def get_collection_summary(self):
        """获取数据收集情况总结"""
        with open(self.log_file, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        
        summary = {
            '总收集次数': len(log_data['collections']),
            '总文件数': log_data['total_files'],
            '最近收集': log_data['collections'][-5:] if log_data['collections'] else [],
            '创建时间': log_data['created_at']
        }
        
        return summary

def main():
    """主函数"""
    print("="*60)
    print("🏥 中医药统计数据收集工具（简化版）")
    print("="*60)
    
    # 初始化收集器
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    collector = SimpleTCMDataCollector(base_dir)
    
    # 创建数据模板
    print("\n📊 创建数据模板...")
    template_path = collector.create_data_template()
    print(f"✅ 模板已创建: {template_path}")
    
    # 创建示例数据
    print("\n📈 生成示例数据...")
    sample_path = collector.create_sample_data()
    print(f"✅ 示例数据已生成: {sample_path}")
    
    # 显示收集情况
    print("\n📋 数据收集情况:")
    summary = collector.get_collection_summary()
    for key, value in summary.items():
        if key != '最近收集':
            print(f"  {key}: {value}")
    
    print("\n✅ 数据收集工具初始化完成！")
    print("📁 数据目录已创建，可以开始收集实际数据。")
    print("\n📋 下一步操作:")
    print("1. 从官方数据源下载统计数据")
    print("2. 使用模板整理收集的数据")
    print("3. 进行数据质量检查和清洗")

if __name__ == '__main__':
    main()