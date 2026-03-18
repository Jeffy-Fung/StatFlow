"use client";

import Link from "next/link";
import { useState, useRef, type FormEvent, type ChangeEvent } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

interface UploadResult {
  _id: string;
  name: string;
  description?: string | null;
  owner: string;
  created_at: string;
  columns: string[];
  row_count: number;
}

export default function UploadPage() {
  // Auth state
  const [token, setToken] = useState("");
  const [authError, setAuthError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Upload state
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [result, setResult] = useState<UploadResult | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);

  async function handleLogin(e: FormEvent) {
    e.preventDefault();
    setAuthError("");
    setLoginLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: loginUsername, password: loginPassword }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setAuthError(body.detail ?? "Login failed");
        return;
      }
      const data = await res.json();
      setToken(data.access_token);
    } catch {
      setAuthError("Could not reach the server");
    } finally {
      setLoginLoading(false);
    }
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0] ?? null;
    if (selected && !selected.name.toLowerCase().endsWith(".csv")) {
      setUploadError("Only CSV files are supported");
      setFile(null);
      e.target.value = "";
      return;
    }
    setUploadError("");
    setFile(selected);
  }

  async function handleUpload(e: FormEvent) {
    e.preventDefault();
    if (!file) {
      setUploadError("Please select a CSV file");
      return;
    }
    setUploadError("");
    setResult(null);
    setUploadLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("name", name);
      if (description) formData.append("description", description);

      const res = await fetch(`${API_BASE}/api/data/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        setUploadError(body.detail ?? "Upload failed");
        return;
      }

      const data: UploadResult = await res.json();
      setResult(data);
      setName("");
      setDescription("");
      setFile(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch {
      setUploadError("Could not reach the server");
    } finally {
      setUploadLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white px-8 py-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <Link href="/" className="text-2xl font-bold text-zinc-900 dark:text-white">
            Stat<span className="text-blue-600">Flow</span>
          </Link>
          {token && (
            <button
              type="button"
              onClick={() => { setToken(""); setResult(null); }}
              className="text-sm text-zinc-500 hover:text-zinc-900 dark:hover:text-white"
            >
              Sign out
            </button>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-3xl px-8 py-12">
        <h1 className="mb-8 text-3xl font-bold text-zinc-900 dark:text-white">Upload Dataset</h1>

        {/* ── Login panel ─────────────────────────────────────────────────── */}
        {!token && (
          <section className="mb-8 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-700 dark:bg-zinc-900">
            <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-white">Sign in to upload</h2>
            <form onSubmit={handleLogin} className="flex flex-col gap-4">
              <div>
                <label htmlFor="login-username" className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Username
                </label>
                <input
                  id="login-username"
                  type="text"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  required
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
                />
              </div>
              <div>
                <label htmlFor="login-password" className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Password
                </label>
                <input
                  id="login-password"
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
                />
              </div>
              {authError && (
                <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                  {authError}
                </p>
              )}
              <button
                type="submit"
                disabled={loginLoading}
                className="rounded-full bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {loginLoading ? "Signing in…" : "Sign in"}
              </button>
            </form>
          </section>
        )}

        {/* ── Upload panel ────────────────────────────────────────────────── */}
        {token && (
          <section className="mb-8 rounded-2xl border border-zinc-200 bg-white p-6 dark:border-zinc-700 dark:bg-zinc-900">
            <h2 className="mb-4 text-lg font-semibold text-zinc-900 dark:text-white">Upload a CSV file</h2>
            <form onSubmit={handleUpload} className="flex flex-col gap-4">
              <div>
                <label htmlFor="dataset-name" className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Dataset name <span className="text-red-500">*</span>
                </label>
                <input
                  id="dataset-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  maxLength={200}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
                />
              </div>
              <div>
                <label htmlFor="dataset-description" className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  Description
                </label>
                <textarea
                  id="dataset-description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-800 dark:text-white"
                />
              </div>
              <div>
                <label htmlFor="dataset-file" className="mb-1 block text-sm font-medium text-zinc-700 dark:text-zinc-300">
                  CSV file <span className="text-red-500">*</span>
                </label>
                <input
                  id="dataset-file"
                  ref={fileRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  required
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm text-zinc-700 file:mr-3 file:rounded-full file:border-0 file:bg-blue-50 file:px-4 file:py-1 file:text-sm file:font-medium file:text-blue-600 hover:file:bg-blue-100 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                />
                <p className="mt-1 text-xs text-zinc-500">UTF-8 encoded CSV with a header row. Max 10 MB.</p>
              </div>
              {uploadError && (
                <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                  {uploadError}
                </p>
              )}
              <button
                type="submit"
                disabled={uploadLoading}
                className="rounded-full bg-blue-600 px-6 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {uploadLoading ? "Uploading…" : "Upload"}
              </button>
            </form>
          </section>
        )}

        {/* ── Result ──────────────────────────────────────────────────────── */}
        {result && (
          <section className="rounded-2xl border border-green-200 bg-green-50 p-6 dark:border-green-800 dark:bg-green-900/20">
            <h2 className="mb-3 text-lg font-semibold text-green-800 dark:text-green-300">
              ✓ Dataset uploaded successfully
            </h2>
            <dl className="grid grid-cols-2 gap-x-6 gap-y-2 text-sm">
              <dt className="font-medium text-zinc-600 dark:text-zinc-400">Name</dt>
              <dd className="text-zinc-900 dark:text-white">{result.name}</dd>
              {result.description && (
                <>
                  <dt className="font-medium text-zinc-600 dark:text-zinc-400">Description</dt>
                  <dd className="text-zinc-900 dark:text-white">{result.description}</dd>
                </>
              )}
              <dt className="font-medium text-zinc-600 dark:text-zinc-400">Owner</dt>
              <dd className="text-zinc-900 dark:text-white">{result.owner}</dd>
              <dt className="font-medium text-zinc-600 dark:text-zinc-400">Rows</dt>
              <dd className="text-zinc-900 dark:text-white">{result.row_count.toLocaleString()}</dd>
              <dt className="font-medium text-zinc-600 dark:text-zinc-400">Columns</dt>
              <dd className="text-zinc-900 dark:text-white">{result.columns.join(", ")}</dd>
              <dt className="font-medium text-zinc-600 dark:text-zinc-400">ID</dt>
              <dd className="font-mono text-xs text-zinc-700 dark:text-zinc-300">{result._id}</dd>
            </dl>
          </section>
        )}
      </main>
    </div>
  );
}
