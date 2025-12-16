def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Convert QA JSON(.gz) to SquarePoints dataset")
    parser.add_argument("--input", required=True, help="Path to input JSON 'questions' list")
    parser.add_argument("--output", required=False, help="Output .json.gz path to save dataset")
    return parser.parse_args()


if __name__ == "__main__":
    from EgoCL.experiment.Visualize.data.exe_loader import load_exe_dataset
    from EgoCL.experiment.Visualize.pyplot.visualize import plot_square_to_png
    from EgoCL.experiment.Visualize.data.loader import get_square, save_dataset
    from pathlib import Path
    args = parse()
    out_dir = Path(args.output).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset = load_exe_dataset(args.input)

    square = get_square(dataset, 0)
    png_path = Path(str(args.output).replace('.json.gz', '.png'))
    plot_square_to_png(square, str(png_path), duration_seconds=dataset["meta"]["duration_seconds"], bins=150)
    save_dataset(dataset, args.output)
    print(f"Saved dataset to {args.output}\nSaved plot to {png_path}")
