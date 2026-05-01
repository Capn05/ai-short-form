"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import { api, Job, Progress } from "@/lib/api";

const STAGE_LABELS = [
  "",
  "Scraping product page",
  "Generating script",
  "Generating video prompts",
  "Generating voiceover",
  "Generating video clips",
  "Composing final video",
];

function parseProductUrl(url: string): { store: string; product: string } {
  try {
    const { hostname, pathname } = new URL(url);
    const store = hostname.replace(".myshopify.com", "").replace(/^www\./, "");
    const parts = pathname.split("/").filter(Boolean);
    const handle = parts[parts.indexOf("products") + 1] ?? "";
    const product = handle.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
    return { store, product: product || url };
  } catch {
    return { store: "", product: url };
  }
}

export default function JobPage() {
  const router = useRouter();
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<(Job & { progress: Progress | null }) | null>(null);
  const [files, setFiles] = useState<string[]>([]);
  const [downloading, setDownloading] = useState<string | null>(null);
  const [error, setError] = useState("");

  const poll = useCallback(async () => {
    try {
      const data = await api.getJob(id);
      setJob(data);
      if (data.status === "done") {
        const { files } = await api.listFiles(id);
        setFiles(files);
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to load job");
    }
  }, [id]);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.replace("/");
      return;
    }
    poll();
  }, [poll, router]);

  useEffect(() => {
    if (!job || job.status === "done" || job.status === "failed") return;
    const t = setInterval(poll, 4000);
    return () => clearInterval(t);
  }, [job, poll]);

  async function download(filename: string) {
    setDownloading(filename);
    try {
      await api.downloadFile(id, filename);
    } catch {
      setError("Download failed");
    } finally {
      setDownloading(null);
    }
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-500">{error}</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-400">Loading...</p>
      </div>
    );
  }

  const percent = job.progress?.percent ?? 0;
  const message = job.progress?.message ?? "Queued...";
  const stage = job.progress?.stage ?? 0;
  const { store, product } = parseProductUrl(job.product_url);

  return (
    <main className="min-h-screen px-4 py-10">
      <div className="max-w-xl mx-auto space-y-8">

        <button
          onClick={() => router.push("/dashboard")}
          className="text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg px-4 py-2 hover:border-gray-400 transition-colors"
        >
          ← Back
        </button>

        <div className="space-y-1">
          <h1 className="text-3xl font-bold">
            {job.status === "done" ? "Video ready" : job.status === "failed" ? "Generation failed" : "Generating..."}
          </h1>
          <p className="text-gray-800 font-medium text-lg">{product}</p>
          <p className="text-gray-400 text-base">{store}</p>
          <a
            href={job.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-400 text-sm hover:text-gray-600 underline underline-offset-2 truncate block"
          >
            {job.product_url}
          </a>
        </div>

        {/* Progress */}
        {(job.status === "queued" || job.status === "running") && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 space-y-4">
            <div className="flex justify-between text-base">
              <span className="text-gray-700">{message}</span>
              <span className="text-gray-400">{percent}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gray-900 h-2 rounded-full transition-all duration-500"
                style={{ width: `${percent}%` }}
              />
            </div>
            <div className="grid grid-cols-6 gap-1 pt-1">
              {STAGE_LABELS.slice(1).map((label, i) => (
                <div
                  key={i}
                  className={`h-1 rounded-full ${i + 1 <= stage ? "bg-gray-900" : "bg-gray-200"}`}
                  title={label}
                />
              ))}
            </div>
            <p className="text-gray-400 text-sm">This takes 8–12 minutes. You can close this tab and come back.</p>
          </div>
        )}

        {/* Done */}
        {job.status === "done" && files.length > 0 && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 space-y-4">
            <p className="text-green-600 font-medium">✓ Your video is ready</p>
            <div className="space-y-2">
              {files.map((f) => (
                <button
                  key={f}
                  onClick={() => download(f)}
                  disabled={downloading === f}
                  className="w-full flex items-center justify-between bg-gray-900 hover:bg-gray-700 text-white rounded-lg px-5 py-4 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span className="text-base font-medium">{f}</span>
                  <span className="text-base font-semibold">
                    {downloading === f ? "Downloading..." : "↓ Download"}
                  </span>
                </button>
              ))}
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="w-full text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg px-4 py-3 hover:border-gray-400 transition-colors"
            >
              Generate another →
            </button>
          </div>
        )}

        {/* Failed */}
        {job.status === "failed" && (
          <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 space-y-3">
            <p className="text-red-500 font-medium">Generation failed</p>
            {job.error && <p className="text-gray-500 text-sm font-mono">{job.error}</p>}
            <button
              onClick={() => router.push("/dashboard")}
              className="text-sm text-gray-400 hover:text-gray-900"
            >
              ← Try again
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
