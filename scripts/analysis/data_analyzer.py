#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中医药统计数据综合分析工具
支持多维度数据分析
"""

import csv
import os
import json
from datetime import datetime

class TCMDataAnalyzer:
    """中医药数据分析器"""
    
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.datasets = {}
        self.load_all_datasets()
    
    def load_all_datasets(self):
        """加载所有数据集"""
        dataset_files = {
            '医院基础': 'tcm_hospital_basic_2011_2024.csv',
            '各省数据': 'tcm_province_data_2024.csv',
            '服务数据': 'tcm_service_data_2011_2024.csv',
            '投入数据': 'tcm_investment_data_2011_2024.csv',
            '人才数据': 'tcm_talent_data_2011_2024.csv',
            '教育数据': 'tcm_education_data_2011_2024.csv',
            '科研数据': 'tcm_research_data_2011_2024.csv',
            '国际合作': 'tcm_international_data_2011_2024.csv',
            '政策数据': 'tcm_policy_data_2011_2024.csv',
            '慢性病': 'chronic_disease_tcm_data_2011_2024.csv',
            '中药材': 'tcm_herbal_medicine_data_2011_2024.csv',
            '养生保健': 'tcm_health_preservation_data_2011_2024.csv'
        }
        
        for name, filename in dataset_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                self.datasets[name] = self.load_csv(filepath)
    
    def load_csv(self, filepath):
        """加载CSV文件"""
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    def analyze_trend(self, dataset_name, indicator, start_year=2011, end_year=2024):
        """分析趋势"""
        if dataset_name not in self.datasets:
            return None
        
        data = self.datasets[dataset_name]
        trend_data = []
        
        for row in data:
            year = int(row.get('年份', 0))
            if start_year <= year <= end_year and indicator in row:
                value = row[indicator]
                try:
                    trend_data.append({
                        'year': year,
                        'value': float(value)
                    })
                except ValueError:
                    continue
        
        if len(trend_data) >= 2:
            # 计算增长率
            first_value = trend_data[0]['value']
            last_value = trend_data[-1]['value']
            total_growth = (last_value - first_value) / first_value * 100
            
            # 计算年均增长率
            years = len(trend_data) - 1
            avg_growth = (pow(last_value / first_value, 1/years) - 1) * 100
            
            return {
                'start_value': first_value,
                'end_value': last_value,
                'total_growth': total_growth,
                'avg_annual_growth': avg_growth,
                'data_points': len(trend_data)
            }
        
        return None
    
    def compare_indicators(self, indicators):
        """对比多个指标"""
        results = {}
        
        for indicator_info in indicators:
            dataset_name = indicator_info['dataset']
            indicator_name = indicator_info['indicator']
            
            trend = self.analyze_trend(dataset_name, indicator_name)
            if trend:
                results[f"{dataset_name}_{indicator_name}"] = trend
        
        return results
    
    def get_summary(self):
        """获取数据集摘要"""
        summary = {
            'total_datasets': len(self.datasets),
            'total_records': sum(len(data) for data in self.datasets.values()),
            'time_range': '2011-2024',
            'datasets_info': []
        }
        
        for name, data in self.datasets.items():
            if data:
                columns = list(data[0].keys())
                summary['datasets_info'].append({
                    'name': name,
                    'records': len(data),
                    'columns': len(columns),
                    'time_range': f"{data[0].get('年份', 'N/A')} - {data[-1].get('年份', 'N/A')}"
                })
        
        return summary
    
    def generate_report(self):
        """生成分析报告"""
        summary = self.get_summary()
        
        report_lines = [
            "=" * 70,
            "📊 中医药统计数据综合分析报告",
            "=" * 70,
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📈 数据集总览:",
            f"  数据集总数: {summary['total_datasets']}个",
            f"  数据记录总数: {summary['total_records']}条",
            f"  时间范围: {summary['time_range']}",
            "",
            "📊 各数据集详情:"
        ]
        
        for ds_info in summary['datasets_info']:
            report_lines.extend([
                f"\n  {ds_info['name']}:",
                f"    记录数: {ds_info['records']}条",
                f"    指标数: {ds_info['columns']}个",
                f"    时间范围: {ds_info['time_range']}"
            ])
        
        # 分析关键指标趋势
        key_indicators = [
            {'dataset': '医院基础', 'indicator': '中医医院数量'},
            {'dataset': '医院基础', 'indicator': '诊疗人次'},
            {'dataset': '投入数据', 'indicator': '总投入'},
            {'dataset': '人才数据', 'indicator': '中医执业医师'}
        ]
        
        report_lines.extend([
            "",
            "=" * 70,
            "📈 关键指标趋势分析:",
            "=" * 70
        ])
        
        for indicator_info in key_indicators:
            trend = self.analyze_trend(indicator_info['dataset'], indicator_info['indicator'])
            if trend:
                report_lines.extend([
                    f"\n{indicator_info['dataset']} - {indicator_info['indicator']}:",
                    f"  起始值: {trend['start_value']:.2f}",
                    f"  终止值: {trend['end_value']:.2f}",
                    f"  总增长率: {trend['total_growth']:.2f}%",
                    f"  年均增长率: {trend['avg_annual_growth']:.2f}%",
                    f"  数据点数: {trend['data_points']}"
                ])
        
        report_lines.extend([
            "",
            "=" * 70,
            "💡 研究建议:",
            "=" * 70,
            "1. 数据质量验证:",
            "   - 对比官方统计数据验证数据准确性",
            "   - 检查数据时间序列的连续性",
            "   - 验证指标之间的逻辑关系",
            "",
            "2. 分析方向建议:",
            "   - 中医药发展趋势分析",
            "   - 医保政策对中医药服务影响",
            "   - 慢性病中医药治疗效果评估",
            "   - 中医药投入产出效率分析",
            "",
            "3. 建模方向建议:",
            "   - 时间序列预测模型",
            "   - 多元回归分析",
            "   - 面板数据分析",
            "   - 政策效果评估模型",
            "",
            "=" * 70,
            "📊 数据准备完成，可以开始分析建模！",
            "=" * 70
        ])
        
        return "\n".join(report_lines)

def main():
    """主函数"""
    base_dir = '/data/data/com.termux/files/home/downloads/statistics-modeling-competition'
    data_dir = os.path.join(base_dir, 'data', 'generated')
    
    # 创建分析器
    analyzer = TCMDataAnalyzer(data_dir)
    
    # 生成报告
    report = analyzer.generate_report()
    print(report)
    
    # 保存报告
    report_file = os.path.join(base_dir, 'data', 'analysis_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存至: {report_file}")
    
    # 保存数据摘要
    summary = analyzer.get_summary()
    summary_file = os.path.join(base_dir, 'data', 'data_summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"📊 数据摘要已保存至: {summary_file}")

if __name__ == '__main__':
    main()