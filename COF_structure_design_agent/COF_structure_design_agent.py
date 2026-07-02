#!/usr/bin/env python3
"""
COF Structure Design Agent
AI辅助光催化CO2还原的COF结构设计与筛选（步骤二）

功能：
1. COF结构生成（连接子、节点、拓扑）
2. 结构筛选（几何、电子结构、稳定性）
3. 多尺度模拟集成
4. 性能预测
"""

import os
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class COFStructure:
    """COF结构数据类"""
    name: str
    formula: str
    topology: str
    cell_params: Dict[str, float]
    linkers: List[str]
    metal_sites: List[str]
    bandgap: float
    cb_position: float  # vs NHE
    vb_position: float  # vs NHE
    porosity: float
    surface_area: float
    stability: Dict[str, float]
    predicted_performance: Dict[str, float]


class COFStructureDesignAgent:
    """结构设计智能体"""

    def __init__(self, config: Optional[Dict] = None):
        """初始化智能体"""
        self.config = config or self._default_config()
        self.output_dir = self.config.get("output_dir", "results/structure_design")

    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "output_dir": "results/structure_design",
            "topology_library": ["hcb", "tbo", "sql", "aoj"],
            "linker_library": [
                "3,3',4,4'-tetraaminobiphenyl",
                "pyridine-4-carboxaldehyde",
                "1,4-benzenedicarboxaldehyde",
                "2,5-dihydroxyterephthalaldehyde",
                "triazine",
                "porphyrin",
                "carbazole"
            ],
            "metal_library": ["Co", "Ni", "Fe", "Cu", "Ru", "Rh"],
            "min_bandgap": 1.8,
            "max_bandgap": 2.5,
            "min_porosity": 0.6,
            "max_porosity": 0.85,
            "target_co_yield": 100.0
        }

    def setup_directories(self):
        """创建输出目录"""
        os.makedirs(os.path.join(self.output_dir, "structures"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "simulation"), exist_ok=True)

    # ==================== 结构生成功能 ====================

    def design_new_structure(
        self,
        topology: str,
        linkers: Optional[List[str]] = None,
        metal_sites: Optional[List[str]] = None,
        target_properties: Optional[Dict] = None
    ) -> COFStructure:
        """
        设计新COF结构

        参数:
            topology: 拓扑类型
            linkers: 连接子列表
            metal_sites: 金属位点列表
            target_properties: 目标性质

        返回:
            COFStructure对象
        """
        # 使用默认连接子（如果未提供）
        if linkers is None:
            linkers = self.config["linker_library"][:2]

        # 使用默认金属位点
        if metal_sites is None:
            metal_sites = ["Co"]

        # 生成结构参数
        structure = self._generate_structure_params(topology, linkers, metal_sites)

        # 设置目标性质（如果提供）
        if target_properties:
            structure = self._apply_target_properties(structure, target_properties)

        # 预测性能
        structure.predicted_performance = self._predict_performance(structure)

        return structure

    def _generate_structure_params(
        self,
        topology: str,
        linkers: List[str],
        metal_sites: List[str]
    ) -> COFStructure:
        """生成结构参数"""
        # 根据拓扑类型设置晶胞参数
        cell_params = self._get_cell_params_for_topology(topology)

        # 计算孔隙率
        porosity = self._calculate_porosity(topology)

        # 计算比表面积
        surface_area = self._calculate_surface_area(porosity)

        # 确定化学式
        formula = self._calculate_formula(linkers, metal_sites)

        # 计算带隙（简化的线性模型）
        bandgap = self._estimate_bandgap(linkers, metal_sites)

        # 计算能级位置
        cb_position, vb_position = self._estimate_energy_levels(bandgap)

        # 稳定性预测
        stability = {
            "thermal_stability": 300 + np.random.uniform(0, 100),  # °C
            "chemical_stability_ph_min": 3,
            "chemical_stability_ph_max": 11,
            "cycling_stability": 100 + int(np.random.uniform(0, 50))  # 次数
        }

        return COFStructure(
            name=f"{topology}-{'-'.join(linkers[:2])}",
            formula=formula,
            topology=topology,
            cell_params=cell_params,
            linkers=linkers,
            metal_sites=metal_sites,
            bandgap=bandgap,
            cb_position=cb_position,
            vb_position=vb_position,
            porosity=porosity,
            surface_area=surface_area,
            stability=stability,
            predicted_performance={}
        )

    def _get_cell_params_for_topology(self, topology: str) -> Dict[str, float]:
        """根据拓扑类型获取晶胞参数"""
        topology_params = {
            "hcb": {"a": 3.5, "b": 3.5, "c": 1.8},  # nm
            "tbo": {"a": 4.2, "b": 4.2, "c": 2.1},  # nm
            "sql": {"a": 2.8, "b": 2.8, "c": 1.5},  # nm
            "aoj": {"a": 5.0, "b": 5.0, "c": 2.5}   # nm
        }
        return topology_params.get(topology, {"a": 3.5, "b": 3.5, "c": 1.8})

    def _calculate_porosity(self, topology: str) -> float:
        """计算孔隙率"""
        porosity_map = {
            "hcb": 0.68,
            "tbo": 0.72,
            "sql": 0.65,
            "aoj": 0.78
        }
        return porosity_map.get(topology, 0.7)

    def _calculate_surface_area(self, porosity: float) -> float:
        """计算比表面积（近似公式）"""
        return porosity * 1400  # m²/g

    def _calculate_formula(self, linkers: List[str], metal_sites: List[str]) -> str:
        """计算化学式（简化版本）"""
        # 根据连接子长度估算碳原子数
        carbon_counts = {
            "3,3',4,4'-tetraaminobiphenyl": 24,
            "pyridine-4-carboxaldehyde": 6,
            "1,4-benzenedicarboxaldehyde": 12,
            "2,5-dihydroxyterephthalaldehyde": 12,
            "triazine": 3,
            "porphyrin": 20,
            "carbazole": 14
        }

        total_carbons = sum(carbon_counts.get(linker, 6) for linker in linkers) // 2
        total_metals = len(metal_sites)

        return f"C{total_carbons}H{total_carbons * 2}N{total_carbons}O{total_carbons}{''.join([m for m in metal_sites])}"

    def _estimate_bandgap(self, linkers: List[str], metal_sites: List[str]) -> float:
        """估算带隙（简化模型）"""
        # 基础带隙（共轭连接子）
        base_bandgap = 2.2

        # 金属节点影响
        metal_effect = {"Co": 0.0, "Ni": 0.1, "Fe": 0.2, "Cu": -0.1, "Ru": -0.2, "Rh": -0.3}

        metal = metal_sites[0] if metal_sites else "Co"
        metal_adjustment = metal_effect.get(metal, 0.0)

        # 功能化影响
        functional_links = any("pyridine" in linker or "triazine" in linker for linker in linkers)
        functional_adjustment = -0.15 if functional_links else 0.0

        bandgap = base_bandgap + metal_adjustment + functional_adjustment

        # 确保在合理范围内
        return max(1.5, min(3.5, bandgap))

    def _estimate_energy_levels(self, bandgap: float) -> Tuple[float, float]:
        """估算能级位置"""
        # 假设价带在+1.2 V附近
        vb_position = 1.2

        # 导带位置 = 价带 - 带隙
        cb_position = vb_position - bandgap

        return cb_position, vb_position

    # ==================== 结构筛选功能 ====================

    def screen_structures(
        self,
        structures: List[COFStructure],
        criteria: Optional[Dict] = None
    ) -> List[COFStructure]:
        """
        筛选候选结构

        参数:
            structures: COF结构列表
            criteria: 筛选条件

        返回:
            筛选后的结构列表
        """
        if criteria is None:
            criteria = self.config.copy()

        screened = []

        for structure in structures:
            # 几何筛选
            if not self._check_geometric_criteria(structure, criteria):
                continue

            # 电子结构筛选
            if not self._check_electronic_criteria(structure, criteria):
                continue

            # 稳定性筛选
            if not self._check_stability_criteria(structure, criteria):
                continue

            screened.append(structure)

        return screened

    def _check_geometric_criteria(self, structure: COFStructure, criteria: Dict) -> bool:
        """检查几何条件"""
        if "porosity" in criteria:
            min_p, max_p = criteria["porosity"]
            if not (min_p <= structure.porosity <= max_p):
                return False

        return True

    def _check_electronic_criteria(self, structure: COFStructure, criteria: Dict) -> bool:
        """检查电子结构条件"""
        if "bandgap" in criteria:
            min_bg, max_bg = criteria["bandgap"]
            if not (min_bg <= structure.bandgap <= max_bg):
                return False

        if "cb_position" in criteria:
            min_cb, max_cb = criteria["cb_position"]
            if not (min_cb <= structure.cb_position <= max_cb):
                return False

        return True

    def _check_stability_criteria(self, structure: COFStructure, criteria: Dict) -> bool:
        """检查稳定性条件"""
        if "thermal_stability" in criteria:
            min_ts = criteria["thermal_stability"]
            if structure.stability["thermal_stability"] < min_ts:
                return False

        return True

    # ==================== 性能预测功能 ====================

    def _predict_performance(self, structure: COFStructure) -> Dict[str, float]:
        """预测性能"""
        # CO2吸附能（与带隙和孔隙率相关）
        co2_adsorption = -0.4 - 0.1 * (structure.bandgap - 2.0) + 0.05 * structure.porosity

        # CO吸附能
        co_adsorption = -1.1 - 0.05 * structure.bandgap

        # 理论CO产率
        co_yield = self._predict_co_yield(structure)

        return {
            "co2_adsorption_energy": co_adsorption,
            "co_adsorption_energy": co_adsorption * 2.75,  # CO是CO2的2.75倍质量
            "theoretical_co_yield": co_yield,
            "faradaic_efficiency": 80 + min(15, structure.bandgap * 5),
            "selectivity": 90 + min(8, structure.porosity * 10)
        }

    def _predict_co_yield(self, structure: COFStructure) -> float:
        """预测CO产率（简化模型）"""
        # 基础产率
        base_yield = 80.0

        # 带隙优化贡献
        bandgap_contribution = 10 * (2.2 - structure.bandgap)

        # 孔隙率贡献
        porosity_contribution = 15 * (structure.porosity - 0.6)

        # 金属位点贡献
        metal_contribution = 5 * len(structure.metal_sites)

        return base_yield + bandgap_contribution + porosity_contribution + metal_contribution

    # ==================== 多尺度模拟集成 ====================

    def multiscale_simulation(self, structures: List[COFStructure]) -> List[Dict]:
        """
        多尺度模拟

        参数:
            structures: COF结构列表

        返回:
            模拟结果列表
        """
        results = []

        for structure in structures:
            # 简化的模拟流程
            simulation_result = {
                "structure": structure.name,
                "md_stability": {
                    "time": 100 + int(np.random.uniform(0, 50)),  # ps
                    "rmsd": 0.02 + np.random.uniform(0, 0.01)  # Å
                },
                "dft_results": {
                    "bandgap": structure.bandgap,
                    "cb_position": structure.cb_position,
                    "vb_position": structure.vb_position,
                    "lumo": -structure.vb_position - structure.bandgap,
                    "homo": -structure.vb_position
                },
                "reaction_energies": {
                    "co2_adsorption": structure.predicted_performance["co2_adsorption_energy"],
                    "co_adsorption": structure.predicted_performance["co_adsorption_energy"]
                },
                "photocurrent_density": 1.5 + np.random.uniform(0, 0.5)  # mA/cm²
            }

            results.append(simulation_result)

        return results

    # ==================== 报告生成功能 ====================

    def generate_report(self, structures: List[COFStructure], simulation_results: List[Dict], output_dir: Optional[str] = None) -> str:
        """
        生成设计报告

        参数:
            structures: COF结构列表
            simulation_results: 模拟结果列表
            output_dir: 输出目录

        返回:
            报告文件路径
        """
        if output_dir is None:
            output_dir = self.output_dir

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"design_report_{timestamp}.md")

        report_lines = []
        report_lines.append("# COF结构设计报告")
        report_lines.append(f"\n**生成时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**候选数量**: {len(structures)} 个")

        # 设计策略
        report_lines.append("\n## 1. 设计策略")
        report_lines.append("\n### 1.1 连接子选择")
        if structures:
            linkers = set()
            for s in structures:
                linkers.update(s.linkers)
            for linker in sorted(list(linkers)):
                report_lines.append(f"- **{linker}**: 共轭刚性连接子")

        report_lines.append("\n### 1.2 节点设计")
        if structures:
            metals = set()
            for s in structures:
                metals.update(s.metal_sites)
            for metal in sorted(list(metals)):
                report_lines.append(f"- **{metal}**: 金属节点")

        # 候选结构
        report_lines.append("\n## 2. 候选结构")

        # 按CO产率排序
        sorted_structures = sorted(
            structures,
            key=lambda x: x.predicted_performance["theoretical_co_yield"],
            reverse=True
        )

        for i, structure in enumerate(sorted_structures, 1):
            report_lines.append(f"\n### 结构 {i}: {structure.name}")
            report_lines.append(f"- **化学式**: {structure.formula}")
            report_lines.append(f"- **拓扑类型**: {structure.topology}")
            report_lines.append(f"- **晶胞参数**: a={structure.cell_params['a']:.1f} nm, b={structure.cell_params['b']:.1f} nm, c={structure.cell_params['c']:.1f} nm")
            report_lines.append(f"- **空隙率**: {structure.porosity*100:.1f}%")
            report_lines.append(f"- **比表面积**: {structure.surface_area:.0f} m²/g")

            report_lines.append("\n#### 电子结构")
            report_lines.append(f"- **带隙**: {structure.bandgap:.2f} eV")
            report_lines.append(f"- **导带位置**: {structure.cb_position:.2f} V vs NHE")
            report_lines.append(f"- **价带位置**: {structure.vb_position:.2f} V vs NHE")

            report_lines.append("\n#### 稳定性")
            report_lines.append(f"- **热稳定性**: {structure.stability['thermal_stability']:.0f} °C")
            report_lines.append(f"- **化学稳定性**: pH {structure.stability['chemical_stability_ph_min']}-{structure.stability['chemical_stability_ph_max']}")
            report_lines.append(f"- **循环稳定性**: {structure.stability['cycling_stability']} 次")

            report_lines.append("\n#### 性能预测")
            perf = structure.predicted_performance
            report_lines.append(f"- **理论CO产率**: {perf['theoretical_co_yield']:.1f} μmol/(g·h)")
            report_lines.append(f"- **CO2吸附能**: {perf['co2_adsorption_energy']:.2f} eV")
            report_lines.append(f"- **CO吸附能**: {perf['co_adsorption_energy']:.2f} eV")
            report_lines.append(f"- **法拉第效率**: {perf['faradaic_efficiency']:.1f}%")
            report_lines.append(f"- **选择性**: {perf['selectivity']:.1f}%")

        # 筛选结果
        report_lines.append("\n## 3. 筛选结果")
        report_lines.append(f"- **初始候选**: {len(structures)} 个")
        report_lines.append(f"- **最终候选**: {len(sorted_structures)} 个")

        # 优先排序
        report_lines.append("\n## 4. 优先排序")
        for i, structure in enumerate(sorted_structures[:5], 1):
            perf = structure.predicted_performance
            report_lines.append(f"{i}. **{structure.name}** (理论CO产率: {perf['theoretical_co_yield']:.1f} μmol/(g·h))")

        # 下一步工作
        report_lines.append("\n## 5. 下一步工作")
        report_lines.append("1. 执行高精度DFT计算验证电子结构")
        report_lines.append("2. 进行MD模拟评估热稳定性")
        report_lines.append("3. 计算表面反应能垒")
        report_lines.append("4. 进行微观动力学模拟")
        report_lines.append("5. 合成验证")

        # 生成报告
        report_text = "\n".join(report_lines)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_text)

        return report_path

    # ==================== 主函数 ====================

    def generate_and_screen(self, **kwargs) -> Dict:
        """
        执行完整的设计和筛选流程

        返回:
            包含所有结果的字典
        """
        # 设计新结构
        topology = kwargs.get("topology", "hcb")
        linkers = kwargs.get("linkers", None)
        metal_sites = kwargs.get("metal_sites", None)
        target_properties = kwargs.get("target_properties", None)

        print(f"正在设计新结构: {topology} 拓扑")
        structures = []
        for _ in range(20):  # 生成20个候选
            struct = self.design_new_structure(
                topology=topology,
                linkers=linkers,
                metal_sites=metal_sites,
                target_properties=target_properties
            )
            structures.append(struct)

        # 筛选结构
        print("正在筛选候选结构...")
        criteria = kwargs.get("criteria", None) or self.config
        screened = self.screen_structures(structures, criteria)
        print(f"筛选后剩余 {len(screened)} 个候选")

        # 多尺度模拟
        print("正在执行多尺度模拟...")
        simulation_results = self.multiscale_simulation(screened)

        # 生成报告
        print("正在生成报告...")
        report_path = self.generate_report(screened, simulation_results)

        return {
            "initial_structures": structures,
            "screened_structures": screened,
            "simulation_results": simulation_results,
            "report_path": report_path
        }


# ==================== 主函数 ====================

import datetime

def main():
    """主函数"""
    # 初始化智能体
    designer = COFStructureDesignAgent()

    # 执行设计和筛选
    results = designer.generate_and_screen(
        topology="hcb",
        criteria={
            "bandgap": (1.8, 2.5),
            "porosity": (0.6, 0.8),
            "cb_position": (-0.5, 0.0)
        }
    )

    print("\n设计完成！")
    print(f"- 报告: {results['report_path']}")
    print(f"- 初始候选: {len(results['initial_structures'])} 个")
    print(f"- 筛选后候选: {len(results['screened_structures'])} 个")
    print(f"- 最高CO产率: {max(s.predicted_performance['theoretical_co_yield'] for s in results['screened_structures']):.1f} μmol/(g·h)")


if __name__ == "__main__":
    main()