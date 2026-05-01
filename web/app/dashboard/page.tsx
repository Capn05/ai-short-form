"use client";
import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { api, Job } from "@/lib/api";

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string; picture: string } | null>(null);
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);

  const loadJobs = useCallback(async () => {
    try {
      setJobs(await api.listJobs());
    } catch {}
  }, []);

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.replace("/");
      return;
    }
    api.me().then(setUser).catch(() => {
      localStorage.removeItem("token");
      router.replace("/");
    });
    loadJobs();
  }, [router, loadJobs]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!url.trim()) return;
    setSubmitting(true);
    try {
      const { job_id } = await api.submitJob(url.trim());
      router.push(`/jobs/${job_id}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  }

  function signOut() {
    localStorage.removeItem("token");
    router.replace("/");
  }

  return (
    <main className="min-h-screen px-4 py-10">
      <div className="max-w-2xl mx-auto space-y-10">

        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">AI Short Form</h1>
          {user && (
            <div className="flex items-center gap-3">
              {user.picture && (
                <img src={user.picture} alt="" className="w-8 h-8 rounded-full" />
              )}
              <span className="text-gray-500 text-sm">{user.name}</span>
              <button onClick={signOut} className="text-gray-400 text-sm hover:text-gray-900">
                Sign out
              </button>
            </div>
          )}
        </div>

        {/* Form */}
        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 space-y-4">
          <h2 className="font-semibold text-xl">Generate a video ad</h2>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-500 mb-1">Shopify product URL</label>
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://yourstore.myshopify.com/products/..."
                required
                className="w-full bg-white border border-gray-300 rounded-lg px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-gray-500"
              />
            </div>
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-gray-900 text-white font-medium py-3 rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? "Submitting..." : "Generate video →"}
            </button>
          </form>
        </div>

        {/* Job history */}
        {jobs.length > 0 && (
          <div className="space-y-3">
            <h2 className="font-semibold text-gray-400 text-sm uppercase tracking-wider">Your videos</h2>
            {jobs.map((job) => {
              const { store, product } = parseProductUrl(job.product_url);
              return (
                <button
                  key={job.id}
                  onClick={() => router.push(`/jobs/${job.id}`)}
                  className="w-full bg-white border border-gray-300 shadow-sm rounded-lg px-4 py-4 text-left hover:bg-gray-50 hover:border-gray-400 transition-colors flex items-center justify-between"
                >
                  <div className="min-w-0">
                    <p className="text-base font-medium text-gray-800 truncate">{product}</p>
                    <p className="text-sm text-gray-400 truncate">{store}</p>
                  </div>
                  <StatusBadge status={job.status} />
                </button>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}

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

function StatusBadge({ status }: { status: Job["status"] }) {
  const colors: Record<Job["status"], string> = {
    queued: "bg-gray-100 text-gray-600",
    running: "bg-blue-50 text-blue-600",
    done: "bg-green-50 text-green-700",
    failed: "bg-red-50 text-red-600",
  };
  return (
    <span className={`text-sm px-2 py-1 rounded-full font-medium ${colors[status]}`}>
      {status}
    </span>
  );
}
