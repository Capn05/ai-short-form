"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";

const VIDEOS = [
  "https://ai-short-form-output.s3.amazonaws.com/public/demo1.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo2.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo3.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo4.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo5.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo6.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo7.mp4",
];

export default function Home() {
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL;
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("token")) setLoggedIn(true);
  }, []);

  return (
    <main className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <nav className="flex justify-end px-6 pt-6">
        {loggedIn ? (
          <button
            onClick={() => router.push("/dashboard")}
            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            Go to dashboard →
          </button>
        ) : (
          <a
            href={`${API}/auth/google`}
            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            Sign in
          </a>
        )}
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-4 pt-16 pb-12 space-y-6">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight max-w-2xl leading-tight">
          Shopify URL{" "}
          <span className="text-gray-400">→</span>{" "}
          UGC video ad in minutes.
        </h1>
        <p className="text-gray-500 text-lg max-w-xl">
          AI-generated b-roll + voiceover — the format that actually performs on Meta and TikTok. No avatars, no lip sync, no uncanny valley. More formats coming soon.
        </p>
        <div className="flex flex-col items-center gap-3">
          <a
            href={`${API}/auth/google`}
            className="flex items-center justify-center gap-3 px-8 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors text-base"
          >
            <GoogleIcon />
            Get started — $6/video
          </a>
          <p className="text-gray-400 text-sm">No subscription. Pay per video.</p>
        </div>
      </section>

      {/* Carousel */}
      <section className="pb-20 px-4">
        <p className="text-center text-gray-700 text-sm font-semibold uppercase tracking-widest mb-8">Example outputs</p>
        <VideoCarousel />
      </section>

      {/* How it works */}
      <section className="px-4 pb-20 max-w-2xl mx-auto space-y-6">
        <p className="text-center text-gray-700 text-sm font-semibold uppercase tracking-widest">How it works</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          {[
            { step: "1", label: "Paste your Shopify product URL" },
            { step: "2", label: "Our AI picks a proven hook, writes the script, and generates footage that looks like real creator content — captions included." },
            { step: "3", label: "Download your MP4 and run it on Meta or TikTok" },
          ].map(({ step, label }) => (
            <div key={step} className="space-y-2">
              <div className="text-3xl font-bold text-gray-700">{step}</div>
              <p className="text-gray-600 text-base">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="px-4 pb-24 flex flex-col items-center gap-4 text-center">
        <h2 className="text-3xl font-bold">Try it on your product</h2>
        <p className="text-gray-500 text-base max-w-sm">Takes 8–12 minutes. $6 per video. No subscription.</p>
        <a
          href={`${API}/auth/google`}
          className="flex items-center justify-center gap-3 px-8 py-3 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-700 transition-colors"
        >
          <GoogleIcon />
          Sign in with Google
        </a>
      </section>
    </main>
  );
}

const CARD_WIDTH = 360;
const CARD_GAP = -40;

function VideoCarousel() {
  const [current, setCurrent] = useState(0);
  const [playing, setPlaying] = useState(false);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartX = useRef<number | null>(null);
  const wheelAccum = useRef(0);
  const wheelTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const go = useCallback((dir: number) => {
    videoRefs.current[current]?.pause();
    setPlaying(false);
    setCurrent((c) => (c + dir + VIDEOS.length) % VIDEOS.length);
  }, [current]);

  function togglePlay() {
    const v = videoRefs.current[current];
    if (!v) return;
    if (v.paused) { v.play(); setPlaying(true); }
    else { v.pause(); setPlaying(false); }
  }

  function onTouchStart(e: React.TouchEvent) {
    touchStartX.current = e.touches[0].clientX;
  }

  function onTouchEnd(e: React.TouchEvent) {
    if (touchStartX.current === null) return;
    const dx = e.changedTouches[0].clientX - touchStartX.current;
    if (Math.abs(dx) > 40) go(dx < 0 ? 1 : -1);
    touchStartX.current = null;
  }

  function onWheel(e: React.WheelEvent) {
    if (Math.abs(e.deltaX) <= Math.abs(e.deltaY)) return;
    e.preventDefault();
    wheelAccum.current += e.deltaX;
    if (wheelTimer.current) clearTimeout(wheelTimer.current);
    wheelTimer.current = setTimeout(() => { wheelAccum.current = 0; }, 150);
    if (Math.abs(wheelAccum.current) > 100) {
      go(wheelAccum.current > 0 ? 1 : -1);
      wheelAccum.current = 0;
    }
  }

  useEffect(() => {
    videoRefs.current.forEach((v, i) => { if (v && i !== current) v.pause(); });
    setPlaying(false);
  }, [current]);

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Track */}
      <div
        className="relative overflow-hidden select-none"
        style={{ width: "100%", height: CARD_WIDTH * (16 / 9) }}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        onWheel={onWheel}
      >
        <div className="absolute inset-0 flex items-center justify-center">
          {VIDEOS.map((src, i) => {
            let dist = i - current;
            if (dist > VIDEOS.length / 2) dist -= VIDEOS.length;
            if (dist < -VIDEOS.length / 2) dist += VIDEOS.length;
            const absDist = Math.abs(dist);
            const scale = absDist === 0 ? 1 : absDist === 1 ? 0.78 : absDist === 2 ? 0.62 : 0.5;
            const opacity = absDist === 0 ? 1 : absDist === 1 ? 0.65 : absDist === 2 ? 0.35 : 0;
            const translateX = dist * (CARD_WIDTH * 0.7);

            return (
              <div
                key={i}
                onClick={() => {
                  if (absDist === 0) togglePlay();
                  else { videoRefs.current[current]?.pause(); setPlaying(false); setCurrent(i); }
                }}
                className="absolute rounded-2xl overflow-hidden bg-gray-200 cursor-pointer"
                style={{
                  width: CARD_WIDTH,
                  height: CARD_WIDTH * (16 / 9),
                  transform: `translateX(${translateX}px) scale(${scale})`,
                  opacity,
                  transition: "transform 0.35s ease, opacity 0.35s ease",
                  zIndex: VIDEOS.length - absDist,
                }}
              >
                <video
                  ref={(el) => { videoRefs.current[i] = el; }}
                  src={src}
                  className="w-full h-full object-cover"
                  loop
                  playsInline
                  preload="metadata"
                />
                {absDist === 0 && !playing && (
                  <div className="absolute inset-0 flex items-center justify-center bg-black/20">
                    <div className="w-12 h-12 rounded-full bg-white/30 backdrop-blur flex items-center justify-center">
                      <svg className="w-5 h-5 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Dots */}
      <div className="flex items-center gap-4">
        <button onClick={() => go(-1)} className="text-gray-400 hover:text-gray-900 transition-colors p-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="flex gap-2">
          {VIDEOS.map((_, i) => (
            <button
              key={i}
              onClick={() => { videoRefs.current[current]?.pause(); setPlaying(false); setCurrent(i); }}
              className={`w-1.5 h-1.5 rounded-full transition-colors ${i === current ? "bg-gray-900" : "bg-gray-300"}`}
            />
          ))}
        </div>
        <button onClick={() => go(1)} className="text-gray-400 hover:text-gray-900 transition-colors p-2">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24">
      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
    </svg>
  );
}
