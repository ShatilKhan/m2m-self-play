# CLI entry point — generate N dialogue outlines and save to output/dialogues.json
# Usage: python run.py --n 5

import argparse
import json
import os
from self_play import run_dialogue


def print_dialogue(idx: int, outline: list):
    """Print one dialogue in Table 5 format: annotation | utterance side by side."""
    print(f"\n{'─' * 70}")
    print(f"  Dialogue {idx + 1}")
    print(f"{'─' * 70}")
    for turn in outline:
        speaker = turn["speaker"]
        annotation = turn["annotation"]
        utterance = turn["utterance"]
        print(f"  [{speaker}] {annotation:<45} | {utterance}")
    print()


def main():
    parser = argparse.ArgumentParser(description="M2M Self-Play — Medical Domain")
    parser.add_argument("--n", type=int, default=3, help="Number of dialogues to generate")
    args = parser.parse_args()

    dialogues = []
    for i in range(args.n):
        outline = run_dialogue()
        dialogues.append(outline)
        print_dialogue(i, outline)

    # Save to output/
    os.makedirs("output", exist_ok=True)
    out_path = "output/dialogues.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dialogues, f, ensure_ascii=False, indent=2)

    print(f"Saved {args.n} dialogue(s) to {out_path}")


if __name__ == "__main__":
    main()
