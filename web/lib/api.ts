const API = process.env.NEXT_PUBLIC_API_URL!;

function token(): string | null {
  return typeof window !== "undefined" ? localStorage.getItem("token") : null;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? res.statusText);
  }
  return res.json();
}

export const api = {
  me: () =>
    request<{ id: number; email: string; name: string; picture: string; credits: number }>("/auth/me"),

  submitJob: (product_url: string) =>
    request<{ job_id: string }>("/jobs", {
      method: "POST",
      body: JSON.stringify({ product_url }),
    }),

  listJobs: () => request<Job[]>("/jobs"),

  getJob: (id: string) =>
    request<Job & { progress: Progress | null }>(`/jobs/${id}`),

  listFiles: (id: string) =>
    request<{ files: string[] }>(`/jobs/${id}/files`),

  downloadFile: async (jobId: string, filename: string) => {
    const res = await request<{ url: string }>(`/jobs/${jobId}/download/${filename}`);
    const a = document.createElement("a");
    a.href = res.url;
    a.download = filename;
    a.click();
  },

  getPacks: () =>
    request<Pack[]>("/payments/packs"),

  createCheckout: (packId: string) =>
    request<{ checkout_url: string }>(`/payments/checkout/${packId}`, { method: "POST" }),
};

export interface Job {
  id: string;
  status: "queued" | "running" | "done" | "failed";
  product_url: string;
  run_id: string | null;
  error: string | null;
  created_at: string;
}

export interface Progress {
  stage: number;
  message: string;
  percent: number;
}

export interface Pack {
  id: string;
  generations: number;
  price_cents: number;
  price_id: string;
  label: string;
  per_video: string;
}
