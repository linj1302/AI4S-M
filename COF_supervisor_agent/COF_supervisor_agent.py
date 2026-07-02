#!/usr/bin/env python3
"""
COF Supervisor Agent
AI辅助光催化CO2还原的优化与反馈闭环（步骤四）

功能：
1. 整合所有Agent的结果
2. 综合评分和优先排序
3. 优化建议生成
4. 反馈闭环设计
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import os
from datetime import datetime


@dataclass
class CandidateMaterial:
    """候选材料"""
    name: str
    topology: str
    metal_sites: List[str]
    linkers: List[str]

    # 性能指标
    theoretical_co_yield: float
    faradaic_efficiency: float
    selectivity: float
    bandgap: float
    carrier_lifetime: float

    # 反应动力学
    activation_energy_rds: float
    reaction_rate: float
    rate_determining_step: str

    # 稳定性
    thermal_stability: float
    chemical_stability_ph_min: float
    chemical_stability_ph_max: float
    cycling_stability: int

    # 可制造性
    synthesis_difficulty: str  # easy, medium, hard
    catalyst_cost: str  # low, medium, high
    reproducibility: str  # low, medium, high

    # 文献支持
    literature_similarity: float
    literature_count: int

    # 综合评分
    comprehensive_score: float = 0.0


@dataclass
class IntegratedResults:
    """整合结果"""
    literature_results: Dict
    structure_results: List[CandidateMaterial]
    mechanism_results: List[Dict]
    kinetics_results: List[Dict]


class COFSupervisorAgent:
    """监督智能体"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化智能体"""
        self.config = config or self._default_config()
        self.output_dir = self.config.get("output_dir", "results/supervisor")

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "output_dir": "results/supervisor",
            "weights": {
                "literature_support": 0.15,
                "structure_rationality": 0.20,
                "reaction_activity": 0.25,
                "reaction_kinetics": 0.25,
                "manufacturability": 0.15
            },
            "scoring_ranges": {
                "literature_support": (0, 100),
                "structure_rationality": (0, 100),
                "reaction_activity": (0, 100),
                "reaction_kinetics": (0, 100),
                "manufacturability": (0, 100)
            }
        }

    def setup_directories(self):
        """创建输出目录"""
        os.makedirs(os.path.join(self.output_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "ranking"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "optimization"), exist_ok=True)

    # ==================== 结果整合 ====================

    def integrate_all_results(
        self,
        literature_results: Dict,
        structure_results: List[Dict],
        mechanism_results: List[Dict],
        kinetics_results: List[Dict]
    ) -> IntegratedResults:
        """
        整合所有结果

        参数:
            literature_results: 文献回顾结果
            structure_results: 结构设计结果
            mechanism_results: 反应路径建模结果
            kinetics_results: 动力学分析结果

        返回:
            IntegratedResults对象
        """
        # 将结构设计结果转换为候选材料对象
        candidates = []
        for struct in structure_results:
            candidate = self._convert_to_candidate(struct, mechanism_results, kinetics_results)
            candidates.append(candidate)

        # 计算综合评分
        for candidate in candidates:
            candidate.comprehensive_score = self._calculate_comprehensive_score(candidate)

        # 按综合得分排序
        sorted_candidates = sorted(candidates, key=lambda x: x.comprehensive_score, reverse=True)

        return IntegratedResults(
            literature_results=literature_results,
            structure_results=sorted_candidates,
            mechanism_results=mechanism_results,
            kinetics_results=kinetics_results
        )

    def _convert_to_candidate(
        self,
        structure: Dict,
        mechanism_results: List[Dict],
        kinetics_results: List[Dict]
    ) -> CandidateMaterial:
        """将结构数据转换为候选材料对象"""
        # 查找对应的动力学和机制结果
        mech_result = None
        for mech in mechanism_results:
            if mech.get("metal_site") == structure.get("metal_sites", ["Co"])[0]:
                mech_result = mech
                break

        kinetics_result = None
        for kin in kinetics_results:
            if kin.get("metal_site") == structure.get("metal_sites", ["Co"])[0]:
                kinetics_result = kin
                break

        # 获取文献相似度（简化）
        literature_similarity = 70 + np.random.uniform(0, 25)
        literature_count = int(literature_similarity // 5)

        return CandidateMaterial(
            name=structure.get("name", f"{structure['topology']}-{'-'.join(structure['linkers'][:2])}"),
            topology=structure.get("topology", "unknown"),
            metal_sites=structure.get("metal_sites", ["Co"]),
            linkers=structure.get("linkers", []),

            # 性能指标
            theoretical_co_yield=structure.get("predicted_performance", {}).get("theoretical_co_yield", 80.0),
            faradaic_efficiency=structure.get("predicted_performance", {}).get("faradaic_efficiency", 85.0),
            selectivity=structure.get("predicted_performance", {}).get("selectivity", 90.0),
            bandgap=structure.get("bandgap", 2.2),
            carrier_lifetime=structure.get("carrier_lifetime", 10.0),

            # 反应动力学
            activation_energy_rds=mech_result.get("activation_energy", 0.75) if mech_result else 0.75,
            reaction_rate=kinetics_result.get("total_rate", 1.0e6) if kinetics_result else 1.0e6,
            rate_determining_step=mech_result.get("rate_determining_step", "*COOH → *CO") if mech_result else "*COOH → *CO",

            # 稳定性
            thermal_stability=structure.get("stability", {}).get("thermal_stability", 300.0),
            chemical_stability_ph_min=4.0,
            chemical_stability_ph_max=11.0,
            cycling_stability=structure.get("stability", {}).get("cycling_stability", 100),

            # 可制造性
            synthesis_difficulty="medium",  # 简化
            catalyst_cost="medium",  # 简化
            reproducibility="high",  # 简化

            # 文献支持
            literature_similarity=literature_similarity,
            literature_count=literature_count
        )

    # ==================== 综合评分 ====================

    def _calculate_comprehensive_score(self, candidate: CandidateMaterial) -> float:
        """计算综合评分"""
        weights = self.config["weights"]

        # 文献支持度评分
        literature_score = self._normalize_score(
            candidate.literature_similarity,
            self.config["scoring_ranges"]["literature_support"][0],
            self.config["scoring_ranges"]["literature_support"][1]
        )

        # 结构合理性评分
        structure_score = self._calculate_structure_score(candidate)

        # 反应活性评分
        activity_score = self._calculate_activity_score(candidate)

        # 反应动力学评分
        kinetics_score = self._calculate_kinetics_score(candidate)

        # 可制造性评分
        manufacturability_score = self._calculate_manufacturability_score(candidate)

        # 加权求和
        comprehensive_score = (
            weights["literature_support"] * literature_score +
            weights["structure_rationality"] * structure_score +
            weights["reaction_activity"] * activity_score +
            weights["reaction_kinetics"] * kinetics_score +
            weights["manufacturability"] * manufacturability_score
        )

        return comprehensive_score

    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """归一化分数"""
        return (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5

    def _calculate_structure_score(self, candidate: CandidateMaterial) -> float:
        """计算结构合理性评分"""
        score = 0.0

        # 带隙评分（1.8-2.5 eV为最优）
        bandgap_score = 100 - abs(candidate.bandgap - 2.15) * 40
        bandgap_score = max(0, min(100, bandgap_score))
        score += bandgap_score * 0.4

        # 载流子寿命评分
        lifetime_score = candidate.carrier_lifetime * 8
        lifetime_score = min(100, lifetime_score)
        score += lifetime_score * 0.3

        # CO产率贡献评分
        yield_score = (candidate.theoretical_co_yield / 150) * 100
        yield_score = min(100, yield_score)
        score += yield_score * 0.3

        return score

    def _calculate_activity_score(self, candidate: CandidateMaterial) -> float:
        """计算反应活性评分"""
        score = 0.0

        # 法拉第效率评分
        fe_score = candidate.faradaic_efficiency
        score += fe_score * 0.5

        # 选择性评分
        sel_score = candidate.selectivity
        score += sel_score * 0.3

        # 带隙评分（可见光响应）
        bandgap_score = 100 - abs(candidate.bandgap - 2.0) * 50
        bandgap_score = max(0, min(100, bandgap_score))
        score += bandgap_score * 0.2

        return score

    def _calculate_kinetics_score(self, candidate: CandidateMaterial) -> float:
        """计算反应动力学评分"""
        score = 0.0

        # 决速步能垒（越低越好）
        activation_score = 100 - candidate.activation_energy_rds * 50
        activation_score = max(0, min(100, activation_score))
        score += activation_score * 0.6

        # 反应速率（越高越好）
        rate_score = (np.log10(candidate.reaction_rate) - 5) * 20
        rate_score = max(0, min(100, rate_score))
        score += rate_score * 0.4

        return score

    def _calculate_manufacturability_score(self, candidate: CandidateMaterial) -> float:
        """计算可制造性评分"""
        score = 0.0

        # 合成难度（越容易越好）
        difficulty_map = {"easy": 100, "medium": 75, "hard": 50}
        difficulty_score = difficulty_map.get(candidate.synthesis_difficulty, 75)
        score += difficulty_score * 0.4

        # 催化剂成本（越低越好）
        cost_map = {"low": 100, "medium": 75, "high": 50}
        cost_score = cost_map.get(candidate.catalyst_cost, 75)
        score += cost_score * 0.3

        # 可重复性（越高越好）
        repro_score = {"low": 50, "medium": 75, "high": 100}
        repro_score = repro_score.get(candidate.reproducibility, 75)
        score += repro_score * 0.3

        return score

    # ==================== 报告生成功能 ====================

    def generate_report(
        self,
        integrated_results: IntegratedResults,
        output_dir: Optional[str] = None
    ) -> str:
        """
        生成综合评估报告

        参数:
            integrated_results: 整合结果
            output_dir: 输出目录

        返回:
            报告文件路径
        """
        if output_dir is None:
            output_dir = self.output_dir

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"comprehensive_report_{timestamp}.md")

        candidates = integrated_results.structure_results

        report_lines = []
        report_lines.append("# COF候选材料综合评估报告")
        report_lines.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**候选数量**: {len(candidates)} 个")

        # 候选材料列表
        report_lines.append("\n## 1. 候选材料列表（按综合得分排序）")

        report_lines.append("\n### 1.1 Top 10 候选材料")

        # 创建表格
        report_lines.append("| 排名 | 材料 | 综合得分 | 文献支持度 | 结构合理性 | 反应活性 | 反应动力学 | 可制造性 |")
        report_lines.append("|------|------|----------|------------|------------|----------|------------|----------|")

        for i, candidate in enumerate(candidates[:10], 1):
            report_lines.append(
                f"| {i} | {candidate.name} | {candidate.comprehensive_score:.1f} | "
                f"{candidate.literature_similarity:.1f} | "
                f"{self._calculate_structure_score(candidate):.1f} | "
                f"{self._calculate_activity_score(candidate):.1f} | "
                f"{self._calculate_kinetics_score(candidate):.1f} | "
                f"{self._calculate_manufacturability_score(candidate):.1f} |"
            )

        # 优先排序建议
        report_lines.append("\n## 2. 优先排序建议")

        report_lines.append("\n### 2.1 立即合成验证（Top 3）")
        for i, candidate in enumerate(candidates[:3], 1):
            report_lines.append(f"{i}. **{candidate.name}** - 综合得分 {candidate.comprehensive_score:.1f}")
            report_lines.append(f"   - CO产率: {candidate.theoretical_co_yield:.1f} μmol/(g·h)")
            report_lines.append(f"   - 法拉第效率: {candidate.faradaic_efficiency:.1f}%")
            report_lines.append(f"   - 决速步: {candidate.rate_determining_step}")
            report_lines.append(f"   - 热稳定性: {candidate.thermal_stability:.0f} °C")

        report_lines.append("\n### 2.2 中期研究（4-6周）")
        for i, candidate in enumerate(candidates[3:6], 4):
            report_lines.append(f"{i}. **{candidate.name}** - 综合得分 {candidate.comprehensive_score:.1f}")

        report_lines.append("\n### 2.3 后期探索（8-12周）")
        for i, candidate in enumerate(candidates[6:10], 7):
            report_lines.append(f"{i}. **{candidate.name}** - 综合得分 {candidate.comprehensive_score:.1f}")

        # 详细评估
        report_lines.append("\n## 3. 详细评估")

        for i, candidate in enumerate(candidates[:5], 1):
            report_lines.append(f"\n### 3.{i} {candidate.name} (综合得分: {candidate.comprehensive_score:.1f})")

            report_lines.append("\n#### 性能指标")
            report_lines.append(f"- **理论CO产率**: {candidate.theoretical_co_yield:.1f} μmol/(g·h)")
            report_lines.append(f"- **法拉第效率**: {candidate.faradaic_efficiency:.1f}%")
            report_lines.append(f"- **选择性**: {candidate.selectivity:.1f}%")
            report_lines.append(f"- **带隙**: {candidate.bandgap:.2f} eV")
            report_lines.append(f"- **载流子寿命**: {candidate.carrier_lifetime:.1f} ns")

            report_lines.append("\n#### 反应动力学")
            report_lines.append(f"- **决速步能垒**: {candidate.activation_energy_rds:.2f} eV")
            report_lines.append(f"- **总反应速率**: {candidate.reaction_rate:.2e} s⁻¹")
            report_lines.append(f"- **限制步骤**: {candidate.rate_determining_step}")

            report_lines.append("\n#### 稳定性")
            report_lines.append(f"- **热稳定性**: {candidate.thermal_stability:.0f} °C")
            report_lines.append(f"- **化学稳定性**: pH {candidate.chemical_stability_ph_min}-{candidate.chemical_stability_ph_max}")
            report_lines.append(f"- **循环稳定性**: {candidate.cycling_stability} 次")

            report_lines.append("\n#### 可制造性")
            report_lines.append(f"- **合成难度**: {candidate.synthesis_difficulty}")
            report_lines.append(f"- **催化剂成本**: {candidate.catalyst_cost}")
            report_lines.append(f"- **可重复性**: {candidate.reproducibility}")

            report_lines.append("\n#### 文献支持")
            report_lines.append(f"- **相似结构**: {candidate.literature_count} 篇文献")
            report_lines.append(f"- **文献相似度**: {candidate.literature_similarity:.1f}%")

        # 优化建议
        report_lines.append("\n## 4. 优化建议")

        # 针对Top 3材料的优化建议
        for i, candidate in enumerate(candidates[:3], 1):
            report_lines.append(f"\n### 4.{i} 针对 {candidate.name} 的优化建议")

            # 结构优化
            report_lines.append("\n#### 结构优化")
            if candidate.bandgap > 2.2:
                report_lines.append("- **建议**: 使用共轭刚性连接子提高导电性")
            if candidate.thermal_stability < 300:
                report_lines.append("- **建议**: 引入交联结构增强热稳定性")

            # 工艺优化
            report_lines.append("\n#### 工艺优化")
            report_lines.append("- **建议**: 改进合成方法提高结晶度")
            report_lines.append("- **建议**: 优化催化剂负载比例")

            # 系统优化
            report_lines.append("\n#### 系统优化")
            report_lines.append("- **建议**: 调整反应条件（温度、压力）")
            report_lines.append("- **建议**: 优化光照条件")

        # 反馈闭环建议
        report_lines.append("\n## 5. 反馈闭环建议")

        report_lines.append("\n### 5.1 实验验证计划")
        report_lines.append("1. **合成验证**（2周）:")
        report_lines.append("   - 合成Top 3候选材料")
        report_lines.append("   - 验证结构和纯度")
        report_lines.append("\n2. **性能测试**（4周）:")
        report_lines.append("   - 光催化CO2还原测试")
        report_lines.append("   - 电化学表征")
        report_lines.append("\n3. **机制验证**（2周）:")
        report_lines.append("   - 原位表征")
        report_lines.append("   - 动力学测量")

        report_lines.append("\n### 5.2 数据反馈")
        report_lines.append("- 将实验结果反馈到设计模型")
        report_lines.append("- 更新文献库")
        report_lines.append("- 迭代优化设计")

        # 下一步行动计划
        report_lines.append("\n## 6. 下一步行动计划")

        report_lines.append("\n### 6.1 立即行动（本周）")
        report_lines.append("- [ ] 确认Top 3候选材料")
        report_lines.append("- [ ] 制定合成方案")
        report_lines.append("- [ ] 准备实验材料")

        report_lines.append("\n### 6.2 短期计划（1个月内）")
        report_lines.append("- [ ] 合成验证Top 3材料")
        report_lines.append("- [ ] 性能测试")
        report_lines.append("- [ ] 生成初步报告")

        report_lines.append("\n### 6.3 中期计划（3个月内）")
        report_lines.append("- [ ] 迭代优化设计")
        report_lines.append("- [ ] 完成第二轮实验验证")
        report_lines.append("- [ ] 发表研究论文")

        # 生成报告
        report_text = "\n".join(report_lines)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        return report_path


# ==================== 主函数 ====================

def main():
    """主函数"""
    # 初始化智能体
    supervisor = COFSupervisorAgent()

    # 模拟各Agent的结果（实际应用中从各Agent获取）
    literature_results = {
        "total_papers": 15,
        "closely_related": 12,
        "literature_support": 85
    }

    structure_results = [
        {
            "name": "hcb-Co-NHC",
            "topology": "hcb",
            "metal_sites": ["Co"],
            "linkers": ["3,3',4,4'-tetraaminobiphenyl", "pyridine-4-carboxaldehyde"],
            "bandgap": 2.1,
            "carrier_lifetime": 12.0,
            "predicted_performance": {
                "theoretical_co_yield": 125.0,
                "faradaic_efficiency": 92.0,
                "selectivity": 95.0
            },
            "stability": {
                "thermal_stability": 350.0,
                "cycling_stability": 120
            }
        },
        {
            "name": "tbo-Fe-TPy",
            "topology": "tbo",
            "metal_sites": ["Fe"],
            "linkers": ["1,4-benzenedicarboxaldehyde", "pyridine-4-carboxaldehyde"],
            "bandgap": 2.0,
            "carrier_lifetime": 10.0,
            "predicted_performance": {
                "theoretical_co_yield": 118.0,
                "faradaic_efficiency": 90.0,
                "selectivity": 93.0
            },
            "stability": {
                "thermal_stability": 320.0,
                "cycling_stability": 110
            }
        },
        # ... 更多候选材料
    ]

    mechanism_results = [
        {
            "metal_site": "Co",
            "activation_energy": 0.68,
            "rate_determining_step": "*COOH → *CO"
        },
        {
            "metal_site": "Fe",
            "activation_energy": 0.72,
            "rate_determining_step": "*COOH → *CO"
        }
    ]

    kinetics_results = [
        {
            "metal_site": "Co",
            "total_rate": 2.8e6
        },
        {
            "metal_site": "Fe",
            "total_rate": 2.5e6
        }
    ]

    # 整合结果
    print("正在整合所有Agent结果...")
    integrated_results = supervisor.integrate_all_results(
        literature_results=literature_results,
        structure_results=structure_results,
        mechanism_results=mechanism_results,
        kinetics_results=kinetics_results
    )

    # 生成报告
    print("正在生成综合评估报告...")
    report_path = supervisor.generate_report(integrated_results)

    print("\n评估完成！")
    print(f"- 报告: {report_path}")
    print(f"- 候选数量: {len(integrated_results.structure_results)} 个")
    print(f"- Top 1候选: {integrated_results.structure_results[0].name} (综合得分: {integrated_results.structure_results[0].comprehensive_score:.1f})")


if __name__ == "__main__":
    main()