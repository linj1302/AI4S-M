#!/usr/bin/env python3
"""
CDRR Literature Review Agent
AI辅助光催化CO2还原的COF结构设计与反应动力学研究 - 文献检索智能体（步骤一）

功能：
1. 智能文献检索（Web of Science, Scopus, Google Scholar）
2. COF结构信息提取
3. 光催化性能数据分析
4. 反应条件参数提取
5. 研究趋势识别
"""

import requests
import pandas as pd
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import re

class CDRRLiteratureAgent:
    """文献检索智能体"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化智能体"""
        self.config = config or self._default_config()
        self.output_dir = self.config.get("output_dir", "literature/CDRR")
        self.setup_directories()

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "min_impact_factor": 15,
            "years_back": 5,
            "max_papers": 10,
            "search_engines": ["web_of_science", "scopus", "google_scholar"],
            "output_dir": "literature/CDRR",
            "include_theoretical": True,
            "include_experimental": True
        }

    def setup_directories(self):
        """创建输出目录"""
        os.makedirs(os.path.join(self.output_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "structured"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "analysis"), exist_ok=True)

    # ==================== 检索功能 ====================

    def search_papers(self, query: str, **kwargs) -> List[Dict]:
        """
        搜索文献

        参数:
            query: 搜索关键词
            min_impact_factor: 最低影响因子
            years_back: 回溯年限
            max_papers: 最大文献数

        返回:
            文献列表
        """
        min_if = kwargs.get("min_impact_factor", self.config["min_impact_factor"])
        years = kwargs.get("years_back", self.config["years_back"])
        max_results = kwargs.get("max_papers", self.config["max_papers"])

        # 搜索不同数据库
        all_results = []

        # Web of Science
        if "web_of_science" in self.config["search_engines"]:
            results = self._search_wos(query, min_if, years)
            all_results.extend(results)

        # Scopus
        if "scopus" in self.config["search_engines"]:
            results = self._search_scopus(query, min_if, years)
            all_results.extend(results)

        # Google Scholar
        if "google_scholar" in self.config["search_engines"]:
            results = self._search_google_scholar(query, years)
            all_results.extend(results)

        # 去重并限制数量
        unique_results = self._deduplicate_results(all_results)
        return unique_results[:max_results]

    def _search_wos(self, query: str, min_if: float, years: int) -> List[Dict]:
        """搜索Web of Science"""
        # 实际应用中需要调用Web of Science API
        # 这里返回模拟数据
        return [
            {
                "title": f"COF-based photocatalyst for CO2 reduction - Study {i+1}",
                "authors": ["Smith, J.", "Doe, A.", "Johnson, B."],
                "journal": "Nature",
                "year": 2020 + i,
                "impact_factor": 69.5,
                "doi": f"10.1038/s41586-0{i+1}0-0000-0",
                "citations": 100 + i * 10,
                "keywords": ["COF", "photocatalyst", "CO2 reduction", "metal site"]
            }
            for i in range(3)
        ]

    def _search_scopus(self, query: str, min_if: float, years: int) -> List[Dict]:
        """搜索Scopus"""
        # 实际应用中需要调用Scopus API
        return []

    def _search_google_scholar(self, query: str, years: int) -> List[Dict]:
        """搜索Google Scholar"""
        # 实际应用中需要调用Google Scholar API
        return []

    # ==================== 信息提取功能 ====================

    def extract_structure_info(self, papers: List[Dict]) -> Dict:
        """
        提取COF结构信息

        参数:
            papers: 文献列表

        返回:
            结构信息字典
        """
        structure_info = {
            "topologies": set(),
            "linkers": set(),
            "nodes": set(),
            "porosity": [],
            "surface_areas": []
        }

        for paper in papers:
            # 提取关键词中的结构信息
            text = " ".join(str(v) for v in paper.values()).lower()

            # 识别拓扑结构
            if "hexagonal" in text:
                structure_info["topologies"].add("hexagonal")
            if "grid" in text or "net" in text:
                structure_info["topologies"].add("grid")
            if "layered" in text:
                structure_info["topologies"].add("layered")

            # 识别连接子
            linkers = ["triazine", "pyrene", "benzene", "porphyrin", "carbazole"]
            for linker in linkers:
                if linker in text:
                    structure_info["linkers"].add(linker)

            # 识别金属节点
            metals = ["cobalt", "nickel", "iron", "copper", "ruthenium", "rhodium"]
            for metal in metals:
                if metal in text:
                    structure_info["nodes"].add(metal)

            # 提取比表面积
            match = re.search(r"surface area[:\s]+(\d+(?:\.\d+)?)\s*m²/g", text)
            if match:
                structure_info["surface_areas"].append(float(match.group(1)))

        return {
            "topologies": sorted(list(structure_info["topologies"])),
            "linkers": sorted(list(structure_info["linkers"])),
            "nodes": sorted(list(structure_info["nodes"])),
            "average_surface_area": sum(structure_info["surface_areas"]) / len(structure_info["surface_areas"]) if structure_info["surface_areas"] else None,
            "porosity": "high" if structure_info["surface_areas"] and sum(structure_info["surface_areas"]) > 800 else "moderate" if structure_info["surface_areas"] else "unknown"
        }

    def extract_performance_data(self, papers: List[Dict]) -> Dict:
        """
        提取光催化性能数据

        参数:
            papers: 文献列表

        返回:
            性能数据字典
        """
        performance_data = {
            "co_yields": [],
            "faradaic_efficiencies": [],
            "band_gaps": [],
            "cb_positions": [],
            "vb_positions": []
        }

        for paper in papers:
            text = " ".join(str(v) for v in paper.values()).lower()

            # 提取CO产率
            match = re.search(r"co\s+yield[:\s]+(\d+(?:\.\d+)?)\s*μmol/(g·h)", text)
            if match:
                performance_data["co_yields"].append(float(match.group(1)))

            # 提取法拉第效率
            match = re.search(r"faradaic\s+efficiency[:\s]+(\d+(?:\.\d+)?)%", text)
            if match:
                performance_data["faradaic_efficiencies"].append(float(match.group(1)))

            # 提取带隙
            match = re.search(r"band\s+gap[:\s]+(\d+(?:\.\d+)?)\s*eV", text)
            if match:
                performance_data["band_gaps"].append(float(match.group(1)))

        return {
            "average_co_yield": sum(performance_data["co_yields"]) / len(performance_data["co_yields"]) if performance_data["co_yields"] else None,
            "average_faradaic_efficiency": sum(performance_data["faradaic_efficiencies"]) / len(performance_data["faradaic_efficiencies"]) if performance_data["faradaic_efficiencies"] else None,
            "average_band_gap": sum(performance_data["band_gaps"]) / len(performance_data["band_gaps"]) if performance_data["band_gaps"] else None,
            "max_co_yield": max(performance_data["co_yields"]) if performance_data["co_yields"] else None,
            "max_faradaic_efficiency": max(performance_data["faradaic_efficiencies"]) if performance_data["faradaic_efficiencies"] else None
        }

    def extract_reaction_conditions(self, papers: List[Dict]) -> Dict:
        """
        提取反应条件信息

        参数:
            papers: 文献列表

        返回:
            反应条件字典
        """
        conditions = {
            "light_sources": set(),
            "solvents": set(),
            "ph_range": [],
            "temperatures": [],
            "pressures": []
        }

        for paper in papers:
            text = " ".join(str(v) for v in paper.values()).lower()

            # 提取光源
            light_sources = ["led", "laser", "sunlight", "xenon lamp"]
            for source in light_sources:
                if source in text:
                    conditions["light_sources"].add(source)

            # 提取溶剂
            solvents = ["water", "ethanol", "acetonitrile", "dmf", "h2o", "meoh"]
            for solvent in solvents:
                if solvent in text:
                    conditions["solvents"].add(solvent)

            # 提取pH
            match = re.search(r"ph[:\s]+(\d+(?:\.\d+)?)", text)
            if match:
                conditions["ph_range"].append(float(match.group(1)))

            # 提取温度
            match = re.search(r"temperature[:\s]+(\d+(?:\.\d+)?)\s*°c", text)
            if match:
                conditions["temperatures"].append(float(match.group(1)))

            # 提取压力
            match = re.search(r"pressure[:\s]+(\d+(?:\.\d+)?)\s*bar", text)
            if match:
                conditions["pressures"].append(float(match.group(1)))

        return {
            "light_sources": sorted(list(conditions["light_sources"])),
            "solvents": sorted(list(conditions["solvents"])),
            "average_ph": sum(conditions["ph_range"]) / len(conditions["ph_range"]) if conditions["ph_range"] else None,
            "average_temperature": sum(conditions["temperatures"]) / len(conditions["temperatures"]) if conditions["temperatures"] else None,
            "average_pressure": sum(conditions["pressures"]) / len(conditions["pressures"]) if conditions["pressures"] else None
        }

    # ==================== 报告生成功能 ====================

    def generate_report(self, papers: List[Dict], structure_info: Dict, performance_data: Dict, conditions: Dict, output_dir: Optional[str] = None) -> str:
        """
        生成文献综述报告

        参数:
            papers: 文献列表
            structure_info: 结构信息
            performance_data: 性能数据
            conditions: 反应条件
            output_dir: 输出目录

        返回:
            报告文件路径
        """
        if output_dir is None:
            output_dir = self.output_dir

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"literature_review_{timestamp}.md")

        report_lines = []
        report_lines.append("# CDRR文献综述报告")
        report_lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**文献数量**: {len(papers)} 篇")

        # 1. COF结构特征
        report_lines.append("\n## 1. COF结构特征")
        report_lines.append("\n### 1.1 拓扑结构")
        if structure_info["topologies"]:
            for topo in structure_info["topologies"]:
                report_lines.append(f"- **{topo}**: 典型拓扑结构")
        else:
            report_lines.append("- 未明确拓扑结构")

        report_lines.append("\n### 1.2 连接子类型")
        if structure_info["linkers"]:
            for linker in structure_info["linkers"]:
                report_lines.append(f"- **{linker}**: 共轭连接子")
        else:
            report_lines.append("- 未明确连接子类型")

        report_lines.append("\n### 1.3 光催化剂节点")
        if structure_info["nodes"]:
            for node in structure_info["nodes"]:
                report_lines.append(f"- **{node}**: 金属位点")
        else:
            report_lines.append("- 未明确节点类型")

        report_lines.append("\n### 1.4 物理性质")
        if structure_info["average_surface_area"]:
            report_lines.append(f"- **平均比表面积**: {structure_info['average_surface_area']:.1f} m²/g")
            report_lines.append(f"- **孔隙率**: {structure_info['porosity'].upper()}")

        # 2. 光催化性能
        report_lines.append("\n## 2. 光催化性能")
        report_lines.append("\n### 2.1 活性指标")
        if performance_data["average_co_yield"]:
            report_lines.append(f"- **平均CO产率**: {performance_data['average_co_yield']:.1f} μmol/(g·h)")
            report_lines.append(f"- **最高CO产率**: {performance_data['max_co_yield']:.1f} μmol/(g·h)")
        else:
            report_lines.append("- 数据缺失")

        if performance_data["average_faradaic_efficiency"]:
            report_lines.append(f"- **平均法拉第效率**: {performance_data['average_faradaic_efficiency']:.1f}%")
            report_lines.append(f"- **最高法拉第效率**: {performance_data['max_faradaic_efficiency']:.1f}%")
        else:
            report_lines.append("- 数据缺失")

        report_lines.append("\n### 2.2 光电化学参数")
        if performance_data["average_band_gap"]:
            report_lines.append(f"- **平均带隙**: {performance_data['average_band_gap']:.2f} eV")
        else:
            report_lines.append("- 数据缺失")

        # 3. 反应条件
        report_lines.append("\n## 3. 反应条件")
        report_lines.append("\n### 3.1 光源")
        if conditions["light_sources"]:
            for source in conditions["light_sources"]:
                report_lines.append(f"- **{source}**: {source.upper()} 光源")
        else:
            report_lines.append("- 未明确光源类型")

        report_lines.append("\n### 3.2 反应体系")
        if conditions["solvents"]:
            for solvent in conditions["solvents"]:
                report_lines.append(f"- **{solvent}**: {solvent.upper()} 溶剂")
        else:
            report_lines.append("- 未明确溶剂")

        if conditions["average_ph"]:
            report_lines.append(f"- **平均pH**: {conditions['average_ph']:.1f}")
        if conditions["average_temperature"]:
            report_lines.append(f"- **平均温度**: {conditions['average_temperature']:.1f} °C")
        if conditions["average_pressure"]:
            report_lines.append(f"- **平均压力**: {conditions['average_pressure']:.1f} bar")

        # 4. 文献列表
        report_lines.append("\n## 4. 文献列表")
        for i, paper in enumerate(papers, 1):
            report_lines.append(f"\n### 文献 {i}")
            report_lines.append(f"- **标题**: {paper['title']}")
            report_lines.append(f"- **作者**: {', '.join(paper['authors'])}")
            report_lines.append(f"- **期刊**: {paper['journal']} ({paper['year']})")
            report_lines.append(f"- **影响因子**: {paper['impact_factor']}")
            report_lines.append(f"- **DOI**: {paper['doi']}")

        # 5. 关键科学问题总结
        report_lines.append("\n## 5. 关键科学问题总结 (KSQ)")
        report_lines.append("\n### KSQ1: 设计高效COFs活性位点的原则是什么？")
        report_lines.append("- **连接子选择**: 共轭刚性连接子有利于电子传输")
        report_lines.append("- **节点设计**: 金属节点提供活性位点，双金属协同可优化电子结构")
        report_lines.append("- **表面修饰**: 配体修饰和缺陷工程可调控活性位点")

        # 生成报告
        report_text = "\n".join(report_lines)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        # 保存结构化数据到Excel
        self._save_structured_data(papers, structure_info, performance_data, conditions)

        return report_path

    def _save_structured_data(self, papers: List[Dict], structure_info: Dict, performance_data: Dict, conditions: Dict):
        """保存结构化数据到Excel"""
        # 文献列表
        papers_df = pd.DataFrame(papers)
        papers_path = os.path.join(self.output_dir, "structured", "papers.xlsx")
        papers_df.to_excel(papers_path, index=False)

        # 结构信息
        structure_df = pd.DataFrame([structure_info])
        structure_path = os.path.join(self.output_dir, "structured", "structure_info.xlsx")
        structure_df.to_excel(structure_path, index=False)

        # 性能数据
        performance_df = pd.DataFrame([performance_data])
        performance_path = os.path.join(self.output_dir, "structured", "performance_data.xlsx")
        performance_df.to_excel(performance_path, index=False)

        # 反应条件
        conditions_df = pd.DataFrame([conditions])
        conditions_path = os.path.join(self.output_dir, "structured", "reaction_conditions.xlsx")
        conditions_df.to_excel(conditions_path, index=False)

    # ==================== 辅助功能 ====================

    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """去重"""
        seen = set()
        unique = []
        for result in results:
            doi = result.get("doi", "")
            if doi and doi not in seen:
                seen.add(doi)
                unique.append(result)
        return unique

    def create_excel_database(self, output_dir: Optional[str] = None):
        """创建Excel数据库"""
        if output_dir is None:
            output_dir = self.output_dir

        # 读取所有Markdown文件
        md_files = [f for f in os.listdir(output_dir) if f.endswith(".md") and f.startswith("literature_review_")]

        all_data = []
        for md_file in md_files:
            # 这里简化处理，实际需要解析Markdown
            all_data.append({
                "file": md_file,
                "date": datetime.now().strftime("%Y-%m-%d")
            })

        # 创建数据库
        if all_data:
            db_df = pd.DataFrame(all_data)
            db_path = os.path.join(output_dir, "excel_database.xlsx")
            db_df.to_excel(db_path, index=False)

    def literature_review(self, **kwargs) -> Dict:
        """
        执行完整的文献回顾流程

        返回:
            包含所有分析结果的字典
        """
        query = kwargs.get("query", "COF photocatalyst CO2 reduction")
        min_if = kwargs.get("min_impact_factor", self.config["min_impact_factor"])
        years = kwargs.get("years_back", self.config["years_back"])
        max_results = kwargs.get("max_papers", self.config["max_papers"])

        # 1. 搜索文献
        print(f"正在搜索文献: {query}")
        papers = self.search_papers(query, min_if=min_if, years_back=years, max_papers=max_results)
        print(f"找到 {len(papers)} 篇文献")

        # 2. 提取结构信息
        print("正在提取结构信息...")
        structure_info = self.extract_structure_info(papers)

        # 3. 提取性能数据
        print("正在提取性能数据...")
        performance_data = self.extract_performance_data(papers)

        # 4. 提取反应条件
        print("正在提取反应条件...")
        conditions = self.extract_reaction_conditions(papers)

        # 5. 生成报告
        print("正在生成报告...")
        report_path = self.generate_report(
            papers=papers,
            structure_info=structure_info,
            performance_data=performance_data,
            conditions=conditions
        )
        print(f"报告已保存: {report_path}")

        return {
            "papers": papers,
            "structure_info": structure_info,
            "performance_data": performance_data,
            "conditions": conditions,
            "report_path": report_path
        }


# ==================== 主函数 ====================

def main():
    """主函数"""
    # 初始化智能体
    agent = CDRRLiteratureAgent()

    # 执行文献回顾
    results = agent.literature_review(
        query="COF photocatalyst CO2 reduction",
        min_impact_factor=15,
        years_back=5,
        max_papers=10
    )

    # 创建Excel数据库
    agent.create_excel_database()

    print("\n文献回顾完成！")
    print(f"- 报告: {results['report_path']}")
    print(f"- 文献数: {len(results['papers'])}")
    print(f"- CO产率: {results['performance_data']['average_co_yield']:.1f} μmol/(g·h)")


if __name__ == "__main__":
    main()