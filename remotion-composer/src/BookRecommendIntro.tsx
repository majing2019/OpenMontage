import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  staticFile,
} from "remotion";

export interface BookRecommendIntroProps {
  /** Array of image paths for the rapid-switch carousel in Phase 2 */
  images: string[];
  /** Book cover image path for Phase 3 reveal */
  coverImage: string;
  /** Hook text displayed in Phase 1, e.g. "今天分享的是" */
  hookText: string;
  /** Book title, e.g. "《小王子》" */
  title: string;
  /** Book author, displayed in Phase 3 */
  author?: string;
  /** Duration of Phase 1 (hook text) in seconds */
  phase1Duration?: number;
  /** Duration of Phase 2 (image carousel + spinning title) in seconds */
  phase2Duration?: number;
  /** Duration of Phase 3 (cover reveal + settled title) in seconds */
  phase3Duration?: number;
  /** Time each carousel image stays on screen in seconds (default: 0.18) */
  switchInterval?: number;
  /** Total intro duration override. Computed from phases if not set. */
  durationInSeconds?: number;
}

export const BookRecommendIntro: React.FC<BookRecommendIntroProps> = ({
  images = [],
  coverImage,
  hookText = "今天分享的是",
  title = "",
  author,
  phase1Duration = 1.5,
  phase2Duration = 2.8,
  phase3Duration = 2.0,
  switchInterval = 0.035,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const totalDuration = phase1Duration + phase2Duration + phase3Duration;
  const phase1Frames = phase1Duration * fps;
  const phase2Frames = phase2Duration * fps;
  const phase3Frames = phase3Duration * fps;

  // ── Phase boundaries ──
  const phase2Start = phase1Frames;
  const phase3Start = phase1Frames + phase2Frames;

  // ═══════════════════════════════════════════════
  // PHASE 1: Hook text fade in (0 → phase2Start)
  // ═══════════════════════════════════════════════
  const hookOpacity = interpolate(
    frame,
    [0, fps * 0.4, phase2Start - fps * 0.3, phase2Start],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const hookY = interpolate(
    frame,
    [0, fps * 0.4],
    [30, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ═══════════════════════════════════════════════
  // PHASE 2: Image carousel + spinning title
  // ═══════════════════════════════════════════════
  const phase2Progress = interpolate(
    frame,
    [phase2Start, phase3Start],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Image carousel: switch every switchInterval seconds
  const imageIndex =
    images.length > 0
      ? Math.floor((frame - phase2Start) / (fps * switchInterval)) % images.length
      : 0;

  // Title rotation: spins during Phase 2, slows and settles in Phase 3
  // During Phase 2: continuous slow rotation (~30 deg/s)
  // During Phase 3: decelerates to 0
  const spinSpeed = 30; // degrees per second
  const spinAnglePhase2 = (frame - phase2Start) / fps * spinSpeed;
  const spinAnglePhase3 = interpolate(
    frame,
    [phase3Start, phase3Start + fps * 0.6],
    [spinAnglePhase2 + spinSpeed * 0.6, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const titleRotation =
    frame < phase2Start
      ? 0
      : frame < phase3Start
      ? spinAnglePhase2
      : spinAnglePhase3;

  // Title scale: pulse during Phase 2
  const titleScalePulse = 1 + Math.sin((frame - phase2Start) * 0.12) * 0.05;
  const titleScalePhase2 =
    frame >= phase2Start && frame < phase3Start ? titleScalePulse : 1;

  // Title position: centered during Phase 2, moves to top during Phase 3
  const titleY = interpolate(
    frame,
    [phase3Start, phase3Start + fps * 0.5],
    [0, -340], // from center to top
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ═══════════════════════════════════════════════
  // PHASE 3: Cover reveal + settled title
  // ═══════════════════════════════════════════════
  const coverScale = spring({
    frame: frame - phase3Start,
    fps,
    config: { damping: 14, stiffness: 80, mass: 0.8 },
  });

  const coverOpacity = interpolate(
    frame,
    [phase3Start, phase3Start + fps * 0.3],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Dim the carousel images as cover appears
  const carouselDim = interpolate(
    frame,
    [phase3Start, phase3Start + fps * 0.3],
    [1, 0.15],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Author text fade in during Phase 3
  const authorOpacity = interpolate(
    frame,
    [phase3Start + fps * 0.4, phase3Start + fps * 0.8],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Overall fade out at the very end
  const fadeOut = interpolate(
    frame,
    [totalDuration * fps - fps * 0.3, totalDuration * fps],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Background: static image in Phase 1, carousel in Phase 2, cover in Phase 3 ──
  const currentBgImage =
    frame < phase2Start
      ? images.length > 0
        ? images[0]
        : coverImage
      : frame < phase3Start
      ? images[imageIndex]
      : coverImage;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0f",
        opacity: fadeOut,
      }}
    >
      {/* ── Background image layer ── */}
      <AbsoluteFill>
        <Img
          src={staticFile(currentBgImage)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity:
              frame < phase3Start
                ? 1
                : coverOpacity > 0.5
                ? 1
                : carouselDim,
          }}
        />
        {/* Dark overlay for text readability */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0.2) 50%, rgba(0,0,0,0.5) 100%)",
          }}
        />
      </AbsoluteFill>

      {/* ── Phase 3: Book cover scaled reveal ── */}
      {frame >= phase3Start && coverImage && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div
            style={{
              width: "55%",
              maxWidth: 600,
              opacity: coverOpacity,
              transform: `scale(${interpolate(coverScale, [0, 1], [0.3, 1])})`,
              borderRadius: 16,
              overflow: "hidden",
              boxShadow:
                "0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(255,255,255,0.05)",
            }}
          >
            <Img
              src={staticFile(coverImage)}
              style={{
                width: "100%",
                height: "auto",
                objectFit: "contain",
              }}
            />
          </div>
        </div>
      )}

      {/* ── Phase 1: Hook text ── */}
      {frame < phase2Start && (
        <div
          style={{
            position: "absolute",
            bottom: "22%",
            left: 0,
            right: 0,
            textAlign: "center",
            opacity: hookOpacity,
            transform: `translateY(${hookY}px)`,
          }}
        >
          <span
            style={{
              fontFamily: "'PingFang SC', 'Noto Sans SC', 'Heiti SC', system-ui, sans-serif",
              fontSize: 36,
              fontWeight: 400,
              color: "#FFFFFF",
              letterSpacing: "0.06em",
              textShadow: "0 2px 12px rgba(0,0,0,0.6)",
            }}
          >
            {hookText}
          </span>
        </div>
      )}

      {/* ── Title: spinning in Phase 2, settles at top in Phase 3 ── */}
      {(frame >= phase2Start || frame < phase3Start + phase3Frames) && (
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: 0,
            right: 0,
            textAlign: "center",
            transform:
              frame < phase3Start
                ? `rotate(${titleRotation}deg) scale(${titleScalePhase2}) translateY(${titleY}px)`
                : `rotate(0deg) translateY(${titleY}px)`,
          }}
        >
          <span
            style={{
              fontFamily:
                "'Songti SC', 'Noto Serif SC', 'STSong', 'SimSun', serif",
              fontSize: frame < phase3Start ? 56 : 48,
              fontWeight: 700,
              color: "#FFFFFF",
              letterSpacing: "0.08em",
              textShadow: "0 2px 20px rgba(0,0,0,0.5)",
            }}
          >
            {title}
          </span>
        </div>
      )}

      {/* ── Phase 3: Author text ── */}
      {author && frame >= phase3Start && (
        <div
          style={{
            position: "absolute",
            bottom: "18%",
            left: 0,
            right: 0,
            textAlign: "center",
            opacity: authorOpacity,
          }}
        >
          <span
            style={{
              fontFamily:
                "'PingFang SC', 'Noto Sans SC', 'Heiti SC', system-ui, sans-serif",
              fontSize: 22,
              fontWeight: 300,
              color: "rgba(255,255,255,0.75)",
              letterSpacing: "0.04em",
            }}
          >
            {author}
          </span>
        </div>
      )}
    </AbsoluteFill>
  );
};
