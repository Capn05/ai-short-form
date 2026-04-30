"use client";
import { useEffect, useRef, useState } from "react";
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

  useEffect(() => {
    if (localStorage.getItem("token")) {
      router.replace("/dashboard");
    }
  }, [router]);

  return (
    <main className="min-h-screen bg-black text-white">
      {/* Hero */}
      <section className="flex flex-col items-center text-center px-4 pt-24 pb-16 space-y-6">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight max-w-2xl leading-tight">
          Paste your Shopify URL.<br />Get a UGC video ad in minutes.
        </h1>
        <p className="text-gray-400 text-lg max-w-xl">
          AI-generated b-roll + voiceover ads that look like real creator content. No actors, no briefs, no waiting.
        </p>
        <div className="flex flex-col items-center gap-3">
          <a
            href={`${API}/auth/google`}
            className="flex items-center justify-center gap-3 px-8 py-3 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors text-base"
          >
            <GoogleIcon />
            Get started — $6/video
          </a>
          <p className="text-gray-600 text-sm">No subscription. Pay per video.</p>
        </div>
      </section>

      {/* Video grid */}
      <section className="px-4 pb-20">
        <p className="text-center text-gray-500 text-sm uppercase tracking-widest mb-8">Example outputs</p>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 max-w-5xl mx-auto">
          {VIDEOS.map((src, i) => (
            <VideoCard key={i} src={src} />
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="px-4 pb-20 max-w-2xl mx-auto space-y-6">
        <p className="text-center text-gray-500 text-sm uppercase tracking-widest">How it works</p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-center">
          {[
            { step: "1", label: "Paste your Shopify product URL" },
            { step: "2", label: "AI writes the script and generates the video" },
            { step: "3", label: "Download your MP4 and run it on Meta or TikTok" },
          ].map(({ step, label }) => (
            <div key={step} className="space-y-2">
              <div className="text-3xl font-bold text-gray-700">{step}</div>
              <p className="text-gray-300 text-sm">{label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Bottom CTA */}
      <section className="px-4 pb-24 flex flex-col items-center gap-4 text-center">
        <h2 className="text-2xl font-bold">Try it on your product</h2>
        <p className="text-gray-400 text-sm max-w-sm">Takes 8–12 minutes. $6 per video. No subscription.</p>
        <a
          href={`${API}/auth/google`}
          className="flex items-center justify-center gap-3 px-8 py-3 bg-white text-gray-900 rounded-lg font-medium hover:bg-gray-100 transition-colors"
        >
          <GoogleIcon />
          Sign in with Google
        </a>
      </section>
    </main>
  );
}

function VideoCard({ src }: { src: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [playing, setPlaying] = useState(false);

  function toggle() {
    const v = videoRef.current;
    if (!v) return;
    if (v.paused) {
      v.play();
      setPlaying(true);
    } else {
      v.pause();
      setPlaying(false);
    }
  }

  return (
    <div
      className="relative aspect-[9/16] bg-gray-900 rounded-xl overflow-hidden cursor-pointer group"
      onClick={toggle}
    >
      <video
        ref={videoRef}
        src={src}
        className="w-full h-full object-cover"
        loop
        playsInline
        preload="metadata"
      />
      {!playing && (
        <div className="absolute inset-0 flex items-center justify-center bg-black/30 group-hover:bg-black/20 transition-colors">
          <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
            <svg className="w-5 h-5 text-white ml-1" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        </div>
      )}
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
