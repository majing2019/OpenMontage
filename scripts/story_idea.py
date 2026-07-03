#!/usr/bin/env python3
"""Story Factory CLI — generate comic story ideas from the command line.

Usage:
    # Inspiration from text
    python scripts/story_idea.py --text "今天上班电梯里放了个屁..."

    # Inspiration from video
    python scripts/story_idea.py --video "https://youtube.com/watch?v=xxx"

    # Original modes
    python scripts/story_idea.py --mode emotion_matrix --emotion 温暖 --scene 地铁
    python scripts/story_idea.py --mode what_if --source "外卖小哥雨中送餐"
    python scripts/story_idea.py --mode daily_catch
    python scripts/story_idea.py --mode batch --count 5
    python scripts/story_idea.py --seed 42 --count 3
    python scripts/story_idea.py --list-patterns
    python scripts/story_idea.py --list-emotions
    python scripts/story_idea.py --output story.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Ensure project root is on path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from tools.writing.story_factory import StoryFactory
from tools.writing._patterns import PATTERNS
from tools.writing._emotion_matrix import EMOTIONS, SCENES


def _print_seed(seed: dict, index: int | None = None) -> None:
    """Pretty-print a story seed to stdout."""
    prefix = f"[{index}] " if index is not None else ""
    print(f"\n{'='*60}")
    print(f"{prefix}《{seed['title']}》")
    print(f"{'='*60}")
    print(f"  模式:   {seed['pattern']} ({seed['pattern_category']})")
    print(f"  难度:   {seed['difficulty']}")
    print(f"  时长:   {seed['target_duration_seconds']}s")
    print(f"  标签:   {', '.join(seed.get('douyin_tags', []))}")
    print(f"  情绪弧: {seed['emotion_arc']['starts']} → {seed['emotion_arc']['peaks_at']} → {seed['emotion_arc']['ends']}")
    print()
    print(f"  🪝 钩子: {seed['hook']}")
    print(f"  📖 一句话: {seed['logline']}")
    print(f"  💡 反转: {seed.get('twist', 'N/A')}")
    print(f"  🎬 结尾: {seed.get('ending', 'N/A')}")
    print()
    print("  📋 五拍结构:")
    for beat in seed["beats"]:
        print(f"    [{beat['start_second']:.0f}-{beat['end_second']:.0f}s] {beat['name']}: {beat['description'][:60]}")
    print()
    print("  👤 角色:")
    for char in seed.get("character_archetypes", []):
        print(f"    · {char['role']}: {char['description']}")
        print(f"      视觉锚定: {char.get('visual_notes', 'N/A')}")
    print()
    style = seed.get("suggested_style", {})
    keywords = style.get("seedream_keywords", [])
    print(f"  🎨 风格: {style.get('mood', 'N/A')} | {style.get('color_palette', 'N/A')}")
    print(f"  🔑 Seedream关键词: {', '.join(keywords)}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Story Factory — 为抖音漫画生成故事创意",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["emotion_matrix", "what_if", "daily_catch", "random", "batch", "from_text", "from_video"],
        default="random",
        help="生成模式 (default: random)",
    )
    parser.add_argument(
        "--emotion", "-e",
        choices=EMOTIONS,
        help="目标情绪 (emotion_matrix模式)",
    )
    parser.add_argument(
        "--scene", "-s",
        choices=SCENES,
        help="场景位置 (emotion_matrix模式)",
    )
    parser.add_argument(
        "--source",
        help="一句话素材 (what_if模式)",
    )
    parser.add_argument(
        "--text", "-t",
        help="文本段子/故事素材 (from_text模式，支持任意长度)",
    )
    parser.add_argument(
        "--video", "-v",
        help="视频URL或本地文件路径 (from_video模式)",
    )
    parser.add_argument(
        "--pattern", "-p",
        help="强制使用的故事模式名称",
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="生成数量 (1-20, default: 1)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="随机种子 (用于复现结果)",
    )
    parser.add_argument(
        "--duration", "-d",
        type=float,
        default=60,
        help="目标时长秒数 (15-90, default: 60)",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出到JSON文件 (不指定则打印到终端)",
    )
    parser.add_argument(
        "--list-patterns",
        action="store_true",
        help="列出所有12个故事模式",
    )
    parser.add_argument(
        "--list-emotions",
        action="store_true",
        help="列出所有情绪和场景",
    )

    args = parser.parse_args()

    # List modes
    if args.list_patterns:
        print("12 个故事模式:\n")
        for p in PATTERNS:
            print(f"  {p.name} ({p.name_en})")
            print(f"    类别: {p.category} | 难度: {p.difficulty}")
            print(f"    {p.description}")
            print(f"    示例: {'; '.join(p.sample_loglines[:2])}")
            print()
        return 0

    if args.list_emotions:
        print(f"情绪 ({len(EMOTIONS)}): {', '.join(EMOTIONS)}")
        print(f"场景 ({len(SCENES)}): {', '.join(SCENES)}")
        return 0

    # Build inputs
    inputs: dict = {
        "mode": args.mode,
        "count": args.count,
        "target_duration_seconds": args.duration,
    }
    if args.emotion:
        inputs["emotion"] = args.emotion
    if args.scene:
        inputs["scene"] = args.scene
    if args.source:
        inputs["source_concept"] = args.source
    if args.text:
        inputs["mode"] = "from_text"
        inputs["text_content"] = args.text
    if args.video:
        inputs["mode"] = "from_video"
        inputs["video_source"] = args.video
    if args.pattern:
        inputs["pattern"] = args.pattern
    if args.seed is not None:
        inputs["seed"] = args.seed

    # Run
    factory = StoryFactory()
    result = factory.execute(inputs)

    if not result.success:
        print(f"Error: {result.error}", file=sys.stderr)
        return 1

    seeds = result.data["seeds"]
    print(f"\n🎬 Story Factory — 生成 {len(seeds)} 个故事种子 (模式: {result.data['generation_mode']})")

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json.dumps(seeds, ensure_ascii=False, indent=2))
        print(f"✅ 已保存到 {out_path}")
    else:
        for i, seed in enumerate(seeds):
            _print_seed(seed, i + 1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
