"use client";
import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";

const VIDEOS = [
  "https://ai-short-form-output.s3.amazonaws.com/public/demo1.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo2.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo3.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo4.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo5.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo6.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo7.mp4",
  "https://ai-short-form-output.s3.amazonaws.com/public/demo8.mp4",
];

export default function Home() {
  const router = useRouter();
  const API = process.env.NEXT_PUBLIC_API_URL;
  const [loggedIn, setLoggedIn] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    if (localStorage.getItem("token")) setLoggedIn(true);
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <main className="min-h-screen bg-white text-gray-900">
      {/* Nav */}
      <nav className={`fixed top-0 left-0 right-0 z-50 flex justify-between items-center px-6 py-3 transition-all duration-300 ${
        scrolled
          ? "bg-white/80 backdrop-blur-md border-b border-gray-200/60 shadow-sm"
          : "bg-transparent"
      }`}>
        <Image src="/logo/logo-light.png" alt="Dropgen" width={scrolled ? 160 : 200} height={scrolled ? 42 : 54} priority style={{ transition: "width 0.3s, height 0.3s" }} />
        {loggedIn ? (
          <button
            onClick={() => router.push("/dashboard")}
            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            Go to dashboard →
          </button>
        ) : (
          <div className="flex items-center gap-3">
            <a
              href={`${API}/auth/google`}
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Log in
            </a>
            <a
              href={`${API}/auth/google`}
              className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition-colors"
            >
              Get started
            </a>
          </div>
        )}
      </nav>
      <div className="h-16" />

      {/* Hero */}
      <section className="flex flex-col items-center text-center px-4 pt-16 pb-12 space-y-6">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight max-w-2xl leading-tight">
          Shopify URL{" "}
          <span className="text-gray-400">→</span>{" "}
          UGC video ad in minutes.
        </h1>
        <p className="text-gray-500 text-lg max-w-xl">
          AI-generated b-roll + voiceover + winning hooks — the AI format that actually performs on Meta and TikTok. No avatars, no choppy lip sync, no uncanny valley.<br></br><br></br> More formats coming soon.
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

      {/* Powered by */}
      <section className="px-4 pb-12 text-center">
        <p className="text-xs text-gray-400 uppercase tracking-widest mb-3">Powered by</p>
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-sm text-gray-500 font-medium">
          <span>ElevenLabs</span>
          <span className="text-gray-300">·</span>
          <span>Seedance 2</span>
          <span className="text-gray-300">·</span>
          <span>GPT-5.5</span>
          <span className="text-gray-300">·</span>
          <span>GPT Images 2.0</span>
        </div>
      </section>

      {/* How it works */}
      <section className="px-4 pb-20 max-w-5xl mx-auto space-y-8">
        <p className="text-center text-gray-700 text-sm font-semibold uppercase tracking-widest">How it works</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">

          {/* Step 1 */}
          <div className="bg-gray-900 rounded-2xl overflow-hidden flex flex-col">
            <div className="p-5 flex-1">
              <CardScrape />
            </div>
            <div className="px-5 pb-5">
              <p className="text-white font-semibold mb-1">Paste your Shopify URL</p>
              <p className="text-gray-400 text-sm">Drop in your product page — we scrape everything we need.</p>
            </div>
          </div>

          {/* Step 2 */}
          <div className="bg-gray-900 rounded-2xl overflow-hidden flex flex-col">
            <div className="p-5 flex-1">
              <CardPipeline />
            </div>
            <div className="px-5 pb-5">
              <p className="text-white font-semibold mb-1">AI writes and films</p>
              <p className="text-gray-400 text-sm">Picks a proven hook, writes the script, generates footage with captions.</p>
            </div>
          </div>

          {/* Step 3 */}
          <div className="bg-gray-900 rounded-2xl overflow-hidden flex flex-col">
            <div className="p-5 flex-1">
              <CardDownload />
            </div>
            <div className="px-5 pb-5">
              <p className="text-white font-semibold mb-1">Download and run</p>
              <p className="text-gray-400 text-sm">Get your MP4 and launch it on TikTok or Meta.</p>
            </div>
          </div>

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

      {/* Footer */}
      <footer className="border-t border-gray-100 px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-gray-400">
        <span>© {new Date().getFullYear()} Dropgen</span>
        <a
          href="mailto:gxalvarado2013@gmail.com"
          className="hover:text-gray-700 transition-colors"
        >
          Questions, feedback, or refunds → gxalvarado2013@gmail.com
        </a>
      </footer>
    </main>
  );
}

const CARD_WIDTH = 360;
const CARD_GAP = -40;

function VideoCarousel() {
  const [current, setCurrent] = useState(0);
  const [muted, setMuted] = useState(true);
  const videoRefs = useRef<(HTMLVideoElement | null)[]>([]);
  const touchStartX = useRef<number | null>(null);
  const wheelAccum = useRef(0);
  const wheelTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const go = useCallback((dir: number) => {
    videoRefs.current[current]?.pause();
    setCurrent((c) => (c + dir + VIDEOS.length) % VIDEOS.length);
  }, [current]);

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
    videoRefs.current.forEach((v, i) => {
      if (!v) return;
      if (i === current) { v.muted = muted; v.play().catch(() => {}); }
      else v.pause();
    });
  }, [current, muted]);

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
                  if (absDist === 0) setMuted(m => !m);
                  else { videoRefs.current[current]?.pause(); setCurrent(i); }
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
                  muted
                  playsInline
                  preload="metadata"
                />
                {absDist === 0 && (
                  <div className="absolute bottom-3 right-3">
                    <div className="w-8 h-8 rounded-full bg-black/40 backdrop-blur flex items-center justify-center">
                      {muted ? (
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M16.5 12A4.5 4.5 0 0014 7.97v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51A8.796 8.796 0 0021 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06A8.99 8.99 0 0017.73 18L19 19.27 20.27 18 5.27 3 4.27 3zM12 4L9.91 6.09 12 8.18V4z"/>
                        </svg>
                      ) : (
                        <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 7.97v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                      )}
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
              onClick={() => { videoRefs.current[current]?.pause(); setCurrent(i); }}
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

const PIPELINE_STAGES = [
  "Scraping product",
  "Writing script",
  "Planning shots",
  "Generating voice",
  "Generating video",
  "Adding captions",
];

const URL_TEXT = "yourstore.myshopify.com/products/vitamin-c-serum";

function CardScrape() {
  const [displayed, setDisplayed] = useState("");
  const [showProduct, setShowProduct] = useState(false);

  useEffect(() => {
    let timeout: ReturnType<typeof setTimeout>;
    let i = 0;

    function loop() {
      setDisplayed("");
      setShowProduct(false);
      i = 0;
      function type() {
        if (i <= URL_TEXT.length) {
          setDisplayed(URL_TEXT.slice(0, i));
          i++;
          timeout = setTimeout(type, 38);
        } else {
          timeout = setTimeout(() => {
            setShowProduct(true);
            timeout = setTimeout(() => loop(), 2500);
          }, 300);
        }
      }
      type();
    }
    loop();
    return () => clearTimeout(timeout);
  }, []);

  return (
    <div className="bg-gray-800 rounded-xl p-4 space-y-3">
      <div className="flex items-center gap-2 bg-gray-700/60 rounded-lg px-3 py-2.5">
        <svg className="w-3 h-3 text-gray-400 shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101M14.828 14.828a4 4 0 015.656 0l4-4a4 4 0 01-5.656-5.656l-1.1 1.1"/>
        </svg>
        <span className="text-gray-300 text-xs font-mono truncate">
          {displayed}<span className="opacity-70">|</span>
        </span>
      </div>
      <div className={`space-y-2 transition-opacity duration-500 ${showProduct ? "opacity-100" : "opacity-0"}`}>
        <p className="text-white text-sm font-medium truncate">Vitamin C Brightening Serum</p>
        <div className="flex items-center gap-2">
          <span className="text-yellow-400 text-xs">★★★★★</span>
          <span className="text-gray-400 text-xs">4.8 · 127 reviews</span>
        </div>
        <span className="text-green-400 text-xs font-medium">$34.99</span>
      </div>
    </div>
  );
}

function CardPipeline() {
  const [active, setActive] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActive(s => (s + 1) % PIPELINE_STAGES.length);
    }, 900);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-800 rounded-xl p-4 space-y-1.5">
      {PIPELINE_STAGES.map((stage, i) => (
        <div
          key={stage}
          className={`flex items-center gap-2.5 rounded-lg px-3 py-1.5 transition-all duration-300 ${
            i === active ? "bg-blue-500/20" : ""
          }`}
        >
          <div className={`w-2 h-2 rounded-full shrink-0 transition-all duration-300 ${
            i === active ? "bg-blue-400 animate-pulse" :
            i < active ? "bg-green-400" : "bg-gray-600"
          }`} />
          <span className={`text-xs transition-colors duration-300 ${
            i === active ? "text-blue-300" :
            i < active ? "text-gray-400" : "text-gray-600"
          }`}>{stage}</span>
          {i < active && (
            <svg className="w-3 h-3 text-green-400 ml-auto" fill="none" stroke="currentColor" strokeWidth={2.5} viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          )}
        </div>
      ))}
    </div>
  );
}

function CardDownload() {
  return (
    <div className="bg-gray-800 rounded-xl p-4 space-y-3">
      <div className="flex justify-center">
        <div className="w-16 rounded-xl bg-gray-700 flex items-center justify-center" style={{ aspectRatio: "9/16", maxHeight: 112 }}>
          <div className="w-7 h-7 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-white ml-0.5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z"/>
            </svg>
          </div>
        </div>
      </div>
      <div className="bg-gray-700/60 rounded-lg px-3 py-2 flex items-center justify-between">
        <span className="text-gray-300 text-xs font-mono">your_ad.mp4</span>
        <svg className="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
        </svg>
      </div>
      <div className="flex gap-2">
        <div className="flex-1 bg-black rounded-lg py-1.5 flex items-center justify-center">
          <span className="text-white text-xs font-bold">TikTok</span>
        </div>
        <div className="flex-1 bg-blue-600 rounded-lg py-1.5 flex items-center justify-center">
          <span className="text-white text-xs font-bold">Meta</span>
        </div>
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
