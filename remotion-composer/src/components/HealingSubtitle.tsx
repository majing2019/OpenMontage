import {
  AbsoluteFill,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/**
 * HealingSubtitle — transparent, centered, Chinese-serif subtitle overlay
 * with smooth fade-in / fade-out. Used by the healing-text pipeline for
 * narration subtitles layered on top of background video clips.
 *
 * The opacity curve uses Remotion's `interpolate` against the Sequence-local
 * frame, so fade timings are independent of the video crossfade rhythm:
 *   - 0 → fadeInFrames:      opacity 0 → 1 (fade IN)
 *   - fadeInFrames → hold:   opacity 1   (full visibility)
 *   - hold → total:          opacity 1 → 0 (fade OUT)
 *
 * A subtle upward drift (12px → 0) accompanies the fade-in for an elegant,
 * "breathing" feel that matches the healing aesthetic.
 */
interface HealingSubtitleProps {
  text: string;
  fontSize?: number;
  color?: string;
  fadeInSeconds?: number;
  fadeOutSeconds?: number;
  /** Segment duration in seconds — used to compute the fade-out start frame. */
  segmentDurationSeconds?: number;
  /** Optional light text-shadow for readability on bright video frames. */
  textShadow?: string;
}

export const HealingSubtitle: React.FC<HealingSubtitleProps> = ({
  text,
  fontSize = 40,
  color = "#3C3833",
  fadeInSeconds = 0.7,
  fadeOutSeconds = 0.5,
  segmentDurationSeconds,
  textShadow = "0 2px 12px rgba(245,240,235,0.7)",
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const fadeInFrames = Math.round(fadeInSeconds * fps);
  const fadeOutFrames = Math.round(fadeOutSeconds * fps);

  // Segment total in frames: prefer the explicit segment duration, else fall
  // back to the composition duration (works when this is the only content).
  const total =
    segmentDurationSeconds != null
      ? Math.round(segmentDurationSeconds * fps)
      : durationInFrames;

  const fadeOutStart = Math.max(fadeInFrames + 1, total - fadeOutFrames);

  const opacity = interpolate(
    frame,
    [0, fadeInFrames, fadeOutStart, total],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  // Gentle upward drift on fade-in (settles as text becomes fully visible)
  const translateY = interpolate(frame, [0, fadeInFrames], [12, 0], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{ justifyContent: "center", alignItems: "center" }}
    >
      <div
        style={{
          opacity,
          transform: `translateY(${translateY}px)`,
          fontSize,
          color,
          // Chinese serif stack — Noto Serif SC (if installed) → macOS Songti
          fontFamily:
            "'Noto Serif SC', 'Songti SC', 'Source Han Serif SC', serif",
          fontWeight: 600,
          textAlign: "center",
          maxWidth: "82%",
          lineHeight: 1.6,
          letterSpacing: "0.02em",
          padding: "0 36px",
          textShadow,
        }}
      >
        {text}
      </div>
    </AbsoluteFill>
  );
};
