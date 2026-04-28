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
        <p className="text-red-400">{error}</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  const percent = job.progress?.percent ?? 0;
  const message = job.progress?.message ?? "Queued...";
  const stage = job.progress?.stage ?? 0;

  return (
    <main className="min-h-screen px-4 py-10">
      <div className="max-w-xl mx-auto space-y-8">

        <button onClick={() => router.push("/dashboard")} className="text-gray-500 text-sm hover:text-white">
          ← Back
        </button>

        <div className="space-y-1">
          <h1 className="text-2xl font-bold">
            {job.status === "done" ? "Video ready" : job.status === "failed" ? "Generation failed" : "Generating..."}
          </h1>
          <p className="text-gray-500 text-sm truncate">{job.product_url}</p>
        </div>

        {/* Progress */}
        {(job.status === "queued" || job.status === "running") && (
          <div className="bg-gray-900 rounded-xl p-6 space-y-4">
            <div className="flex justify-between text-sm">
              <span className="text-gray-300">{message}</span>
              <span className="text-gray-500">{percent}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className="bg-white h-2 rounded-full transition-all duration-500"
                style={{ width: `${percent}%` }}
              />
            </div>
            <div className="grid grid-cols-6 gap-1 pt-1">
              {STAGE_LABELS.slice(1).map((label, i) => (
                <div
                  key={i}
                  className={`h-1 rounded-full ${i + 1 <= stage ? "bg-white" : "bg-gray-800"}`}
                  title={label}
                />
              ))}
            </div>
            <p className="text-gray-600 text-xs">This takes 8–12 minutes. You can close this tab and come back.</p>
          </div>
        )}

        {/* Done */}
        {job.status === "done" && files.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-6 space-y-4">
            <p className="text-green-400 font-medium">✓ Your video is ready</p>
            <div className="space-y-2">
              {files.map((f) => (
                <button
                  key={f}
                  onClick={() => download(f)}
                  disabled={downloading === f}
                  className="w-full flex items-center justify-between bg-gray-800 hover:bg-gray-700 rounded-lg px-4 py-3 transition-colors disabled:opacity-50"
                >
                  <span className="text-sm font-mono text-gray-300">{f}</span>
                  <span className="text-sm text-gray-500">
                    {downloading === f ? "Downloading..." : "Download ↓"}
                  </span>
                </button>
              ))}
            </div>
            <button
              onClick={() => router.push("/dashboard")}
              className="w-full text-sm text-gray-500 hover:text-white pt-2"
            >
              Generate another →
            </button>
          </div>
        )}

        {/* Failed */}
        {job.status === "failed" && (
          <div className="bg-gray-900 rounded-xl p-6 space-y-3">
            <p className="text-red-400 font-medium">Generation failed</p>
            {job.error && <p className="text-gray-500 text-sm font-mono">{job.error}</p>}
            <button
              onClick={() => router.push("/dashboard")}
              className="text-sm text-gray-500 hover:text-white"
            >
              ← Try again
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
