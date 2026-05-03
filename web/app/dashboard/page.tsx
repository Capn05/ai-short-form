"use client";
import { Suspense, useState, useEffect, useCallback } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import { api, Job, Pack } from "@/lib/api";

export default function Dashboard() {
  return (
    <Suspense>
      <DashboardContent />
    </Suspense>
  );
}

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<{ name: string; picture: string; credits: number } | null>(null);
  const [url, setUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [showBuyModal, setShowBuyModal] = useState(false);
  const [packs, setPacks] = useState<Pack[]>([]);
  const [buyingPack, setBuyingPack] = useState<string | null>(null);
  const [paymentSuccess, setPaymentSuccess] = useState(false);

  const loadUser = useCallback(async () => {
    try {
      const u = await api.me();
      setUser(u);
    } catch {
      localStorage.removeItem("token");
      router.replace("/");
    }
  }, [router]);

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
    loadUser();
    loadJobs();
    api.getPacks().then(setPacks).catch(() => {});
  }, [router, loadUser, loadJobs]);

  useEffect(() => {
    if (searchParams.get("payment") === "success") {
      setPaymentSuccess(true);
      const t1 = setTimeout(() => loadUser(), 3000);
      const t2 = setTimeout(() => setPaymentSuccess(false), 6000);
      return () => { clearTimeout(t1); clearTimeout(t2); };
    }
  }, [searchParams, loadUser]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!url.trim()) return;
    if (!user?.credits) {
      setShowBuyModal(true);
      return;
    }
    setSubmitting(true);
    try {
      const { job_id } = await api.submitJob(url.trim());
      router.push(`/jobs/${job_id}`);
    } catch (err: unknown) {
      if (err instanceof Error && err.message.includes("402")) {
        setShowBuyModal(true);
      } else {
        setError(err instanceof Error ? err.message : "Something went wrong");
      }
      setSubmitting(false);
    }
  }

  async function buyPack(packId: string) {
    setBuyingPack(packId);
    try {
      const { checkout_url } = await api.createCheckout(packId);
      window.location.href = checkout_url;
    } catch {
      setBuyingPack(null);
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
          <Image src="/logo/logo-light.png" alt="Dropgen" width={120} height={32} />
          {user && (
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowBuyModal(true)}
                className="text-sm font-medium bg-gray-900 text-white px-3 py-1.5 rounded-lg hover:bg-gray-700 transition-colors"
              >
                {user.credits} credit{user.credits !== 1 ? "s" : ""} · Buy more
              </button>
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

        {/* Payment success banner */}
        {paymentSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-green-700 text-sm">
            Payment successful! Your credits have been added.
          </div>
        )}

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
              {submitting
                ? "Submitting..."
                : user?.credits
                ? "Generate video →"
                : "Buy credits to generate →"}
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

      {/* Buy credits modal */}
      {showBuyModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-6 w-full max-w-md space-y-5">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">Buy credits</h2>
              <button onClick={() => setShowBuyModal(false)} className="text-gray-400 hover:text-gray-900 text-2xl leading-none">×</button>
            </div>
            <p className="text-gray-500 text-sm">Each credit = one video generation. Credits never expire.</p>
            <div className="space-y-3">
              {packs.map((pack) => (
                <button
                  key={pack.id}
                  onClick={() => buyPack(pack.id)}
                  disabled={buyingPack !== null}
                  className="w-full border border-gray-200 rounded-xl px-4 py-4 text-left hover:border-gray-400 hover:bg-gray-50 transition-colors disabled:opacity-50 flex items-center justify-between"
                >
                  <div>
                    <p className="font-semibold text-gray-900">{pack.label}</p>
                    <p className="text-sm text-gray-400">{pack.per_video}</p>
                  </div>
                  <p className="font-bold text-gray-900">
                    ${(pack.price_cents / 100).toFixed(2)}
                    {buyingPack === pack.id && <span className="ml-2 text-gray-400 font-normal text-sm">...</span>}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
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
