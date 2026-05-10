#!/usr/bin/env python3
"""Compute 12x12 metric correlations from two LaTeX result tables.

This script parses `sup_ac.tex` and `sup_pe.tex`, extracts per-method values
across three benchmarks, computes pairwise Pearson correlations among 12
metrics (with pairwise-complete observations), and saves a heatmap plus CSVs.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
	import seaborn as sns
except ModuleNotFoundError:
	sns = None

BENCHMARKS = ["Egoschema", "EgoLifeQA", "EgoR1Bench"]

METRIC_ALIAS: Dict[str, str] = {
	r"\overline{\alpha^c}": "alpha_c",
	r"\overline{\alpha^e_E}": "alpha_eE",
	r"\overline{\theta^e}": "theta_e",
	r"\overline{\alpha^e_C}": "alpha_eC",
	r"\overline{\alpha^{e+}_C}": "alpha_eplus_C",
	r"\overline{\alpha^e_J}": "alpha_eJ",
	r"\overline{\delta^c}": "delta_c",
	r"\overline{\delta^e}": "delta_e",
	r"\overline{\delta^m_\tau}": "delta_m_tau",
	r"\overline{\delta^c_\tau}": "delta_c_tau",
	r"\overline{\delta^e_\tau}": "delta_e_tau",
	r"\overline{\eta^{\mathcal{M}}_{\mathcal{V}}}": "eta_M_V",
}

METRIC_ORDER = [
	"alpha_c",
	"alpha_eE",
	"theta_e",
	"alpha_eC",
	"alpha_eplus_C",
	"alpha_eJ",
	"delta_c",
	"delta_e",
	"delta_m_tau",
	"delta_c_tau",
	"delta_e_tau",
	"eta_M_V",
]

DISPLAY_LABELS: Dict[str, str] = {
	"alpha_c": r"$\overline{\alpha^c}$",
	"alpha_eE": r"$\overline{\alpha^e_E}$",
	"theta_e": r"$\overline{\theta^e}$",
	"alpha_eC": r"$\overline{\alpha^e_C}$",
	"alpha_eplus_C": r"$\overline{\alpha^{e+}_C}$",
	"alpha_eJ": r"$\overline{\alpha^e_J}$",
	"delta_c": r"$\overline{\delta^c}$",
	"delta_e": r"$\overline{\delta^e}$",
	"delta_m_tau": r"$\overline{\delta^m_\tau}$",
	"delta_c_tau": r"$\overline{\delta^c_\tau}$",
	"delta_e_tau": r"$\overline{\delta^e_\tau}$",
	"eta_M_V": r"$\overline{\eta^{\mathcal{M}}_{\mathcal{V}}}$",
}


def normalize_metric_token(cell: str) -> str:
	token = cell.strip().strip("$")
	token = token.replace(" ", "")
	return token


def normalize_method_name(cell: str) -> str:
	name = cell.strip()
	name = re.sub(r"~?\\cite\{[^}]*\}", "", name)
	name = name.replace("{", "").replace("}", "")
	return name.strip()


def parse_value(cell: str) -> Optional[float]:
	value = cell.strip()
	value = value.replace("$", "")
	value = value.replace(" ", "")
	value = value.replace(",", ".")
	if value in {"", "--", "-", "---"}:
		return None
	try:
		return float(value)
	except ValueError:
		return None


def iter_latex_rows(tex_text: str) -> Iterable[str]:
	main_text = tex_text.split(r"\iffalse", 1)[0]
	for chunk in main_text.split(r"\\"):
		row = " ".join(chunk.split())
		row = re.sub(r"^(\\hline\s*)+", "", row).strip()
		if row:
			yield row


def parse_tex_table(tex_path: Path) -> pd.DataFrame:
	text = tex_path.read_text(encoding="utf-8")
	records: List[Dict[str, object]] = []
	current_metric_triplet: Optional[List[str]] = None

	for row in iter_latex_rows(text):
		if row.startswith("%"):
			continue

		if "\\textbf{Metric}" in row:
			parts = [part.strip() for part in row.split("&")]
			metric_cells = [normalize_metric_token(part) for part in parts if "$" in part]
			if len(metric_cells) >= 3:
				current_metric_triplet = [METRIC_ALIAS.get(metric_cells[i], metric_cells[i]) for i in range(3)]
			continue

		if current_metric_triplet is None or "&" not in row:
			continue

		if any(token in row for token in ["\\begin{", "\\end{", "\\caption", "\\label", "\\multicolumn"]):
			continue

		parts = [part.strip() for part in row.split("&")]
		if len(parts) < 11:
			continue

		first_cell = parts[0]
		if any(token in first_cell for token in ["Benchmark", "Metric", "Unit", "Source/Trail"]):
			continue
		if first_cell.lstrip().startswith("%"):
			continue

		first_cell = re.sub(r"^(\\[A-Za-z]+\s*)+", "", first_cell).strip()
		method = normalize_method_name(first_cell)
		if not method:
			continue

		value_cells = parts[2:11]
		if len(value_cells) != 9:
			continue

		for benchmark_idx, benchmark in enumerate(BENCHMARKS):
			for metric_idx, metric_name in enumerate(current_metric_triplet):
				raw_value = value_cells[benchmark_idx * 3 + metric_idx]
				records.append(
					{
						"method": method,
						"benchmark": benchmark,
						"metric": metric_name,
						"value": parse_value(raw_value),
					}
				)

	return pd.DataFrame.from_records(records)


def build_merged_dataframe(ac_path: Path, pe_path: Path) -> pd.DataFrame:
	df_ac = parse_tex_table(ac_path)
	df_pe = parse_tex_table(pe_path)
	merged = pd.concat([df_ac, df_pe], ignore_index=True)
	merged = merged.dropna(subset=["metric"])
	return merged


def compute_correlation(
	merged_df: pd.DataFrame,
	min_periods: int,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
	wide = merged_df.pivot_table(
		index=["method", "benchmark"],
		columns="metric",
		values="value",
		aggfunc="first",
	)
	ordered_columns = [metric for metric in METRIC_ORDER if metric in wide.columns]
	wide = wide.reindex(columns=ordered_columns)

	corr = wide.corr(method="pearson", min_periods=min_periods)
	availability = wide.notna().astype(int)
	counts = availability.T.dot(availability)

	return wide, corr, counts


def save_heatmap(corr_df: pd.DataFrame, output_path: Path) -> None:
	if sns is not None:
		plt.figure(figsize=(10, 8))
		sns.set_style("white")
		sns.heatmap(
			corr_df,
			cmap="RdBu_r",
			vmin=-1,
			vmax=1,
			annot=True,
			fmt=".2f",
			square=True,
			linewidths=0.5,
			linecolor="white",
			cbar_kws={"label": "Pearson r"},
			mask=corr_df.isna(),
		)
		# plt.title("Metric Correlation Heatmap (12x12)")
		plt.xticks(rotation=45, ha="right")
		plt.yticks(rotation=0)
		plt.tight_layout()
		plt.savefig(output_path, dpi=300)
		plt.close()
		return

	fig, ax = plt.subplots(figsize=(10, 8))
	cmap = plt.get_cmap("RdBu_r").copy()
	cmap.set_bad(color="lightgray")
	data = np.ma.masked_invalid(corr_df.to_numpy(dtype=float))
	image = ax.imshow(data, cmap=cmap, vmin=-1, vmax=1, aspect="equal")

	x_labels = corr_df.columns.tolist()
	y_labels = corr_df.index.tolist()
	ax.set_xticks(np.arange(len(x_labels)))
	ax.set_yticks(np.arange(len(y_labels)))
	ax.set_xticklabels(x_labels, rotation=45, ha="right")
	ax.set_yticklabels(y_labels)

	for i in range(corr_df.shape[0]):
		for j in range(corr_df.shape[1]):
			value = corr_df.iat[i, j]
			if pd.notna(value):
				text_color = "white" if abs(value) > 0.5 else "black"
				ax.text(j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=8)

	# ax.set_title("Metric Correlation Heatmap (12x12)")
	# ax.set_xlabel("Metric")
	# ax.set_ylabel("Metric")

	cbar = fig.colorbar(image, ax=ax)
	cbar.set_label("Pearson Correlation Coefficient")

	fig.tight_layout()
	fig.savefig(output_path, dpi=300)
	plt.close(fig)


def apply_display_labels(df: pd.DataFrame) -> pd.DataFrame:
	labels = [DISPLAY_LABELS.get(col, col) for col in df.columns]
	renamed = df.copy()
	renamed.columns = labels
	renamed.index = [DISPLAY_LABELS.get(idx, idx) for idx in renamed.index]
	return renamed


def parse_args() -> argparse.Namespace:
	script_dir = Path(__file__).resolve().parent
	parser = argparse.ArgumentParser(
		description="Compute 12x12 metric correlations from sup_ac.tex and sup_pe.tex."
	)
	parser.add_argument(
		"--ac-tex",
		type=Path,
		default=script_dir / "sup_ac.tex",
		help="Path to the accuracy metrics LaTeX table.",
	)
	parser.add_argument(
		"--pe-tex",
		type=Path,
		default=script_dir / "sup_pe.tex",
		help="Path to the performance metrics LaTeX table.",
	)
	parser.add_argument(
		"--output-dir",
		type=Path,
		default=script_dir,
		help="Output directory for CSV files and heatmap image.",
	)
	parser.add_argument(
		"--min-periods",
		type=int,
		default=3,
		help="Minimum paired samples required for pairwise correlation.",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()
	args.output_dir.mkdir(parents=True, exist_ok=True)

	merged_df = build_merged_dataframe(args.ac_tex, args.pe_tex)
	if merged_df.empty:
		raise RuntimeError("No rows were parsed from the provided TeX tables.")

	wide_df, corr_df, counts_df = compute_correlation(merged_df, min_periods=args.min_periods)

	long_path = args.output_dir / "correlation_long.csv"
	wide_path = args.output_dir / "correlation_wide.csv"
	corr_path = args.output_dir / "correlation_matrix.csv"
	corr_named_path = args.output_dir / "correlation_matrix_symbolic.csv"
	counts_path = args.output_dir / "correlation_counts.csv"
	counts_named_path = args.output_dir / "correlation_counts_symbolic.csv"
	heatmap_path = args.output_dir / "correlation_heatmap.png"

	corr_display_df = apply_display_labels(corr_df)
	counts_display_df = apply_display_labels(counts_df)

	merged_df.to_csv(long_path, index=False)
	wide_df.to_csv(wide_path)
	corr_df.to_csv(corr_path, float_format="%.6f")
	corr_display_df.to_csv(corr_named_path, float_format="%.6f")
	counts_df.to_csv(counts_path)
	counts_display_df.to_csv(counts_named_path)
	save_heatmap(corr_display_df, heatmap_path)

	print(f"Methods: {merged_df['method'].nunique()}")
	print(f"Benchmarks: {merged_df['benchmark'].nunique()}")
	print(f"Metrics: {merged_df['metric'].nunique()}")
	print(f"Method-benchmark points: {len(wide_df)}")
	print("Saved files:")
	print(f"- {long_path}")
	print(f"- {wide_path}")
	print(f"- {corr_path}")
	print(f"- {corr_named_path}")
	print(f"- {counts_path}")
	print(f"- {counts_named_path}")
	print(f"- {heatmap_path}")


if __name__ == "__main__":
	main()
