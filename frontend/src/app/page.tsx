import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col bg-zinc-50 dark:bg-zinc-950">
      {/* Header */}
      <header className="border-b border-zinc-200 bg-white px-8 py-4 dark:border-zinc-800 dark:bg-zinc-900">
        <div className="mx-auto flex max-w-6xl items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl font-bold text-zinc-900 dark:text-white">
              Stat<span className="text-blue-600">Flow</span>
            </span>
          </div>
          <nav className="flex items-center gap-6 text-sm font-medium text-zinc-600 dark:text-zinc-400">
            <a href="#features" className="hover:text-zinc-900 dark:hover:text-white">
              Features
            </a>
            <button type="button" className="hover:text-zinc-900 dark:hover:text-white">
              Docs
            </button>
            <Link
              href="/upload"
              className="rounded-full bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <main className="flex flex-1 flex-col items-center justify-center px-8 py-24 text-center">
        <h1 className="mb-4 text-5xl font-bold tracking-tight text-zinc-900 dark:text-white">
          Statistical Analysis,{" "}
          <span className="text-blue-600">Simplified</span>
        </h1>
        <p className="mb-8 max-w-xl text-lg text-zinc-600 dark:text-zinc-400">
          StatFlow is a comprehensive statistical analysis and data visualization
          tool designed to help researchers and analysts interpret complex
          datasets with ease.
        </p>
        <div className="flex gap-4">
          <Link
            href="/upload"
            className="rounded-full bg-blue-600 px-6 py-3 font-medium text-white hover:bg-blue-700"
          >
            Start Analyzing
          </Link>
          <a
            href="#features"
            className="rounded-full border border-zinc-300 px-6 py-3 font-medium text-zinc-700 hover:border-zinc-400 dark:border-zinc-700 dark:text-zinc-300 dark:hover:border-zinc-500"
          >
            Learn More
          </a>
        </div>
      </main>

      {/* Features */}
      <section
        id="features"
        className="border-t border-zinc-200 bg-white px-8 py-20 dark:border-zinc-800 dark:bg-zinc-900"
      >
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-12 text-center text-3xl font-bold text-zinc-900 dark:text-white">
            Key Features
          </h2>
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {[
              {
                title: "Statistical Analysis",
                description:
                  "Perform various statistical tests and analysis techniques on your data.",
                icon: "📊",
              },
              {
                title: "Visualizations",
                description:
                  "Generate interactive plots and charts to better understand your data.",
                icon: "📈",
              },
              {
                title: "User Management",
                description:
                  "Secure login and user management to keep your data safe.",
                icon: "🔒",
              },
              {
                title: "API Access",
                description:
                  "Access the backend via a RESTful API for seamless integration.",
                icon: "🔌",
              },
            ].map((feature) => (
              <div
                key={feature.title}
                className="rounded-2xl border border-zinc-200 p-6 dark:border-zinc-700"
              >
                <div className="mb-3 text-3xl">{feature.icon}</div>
                <h3 className="mb-2 font-semibold text-zinc-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-sm text-zinc-600 dark:text-zinc-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-200 px-8 py-6 text-center text-sm text-zinc-500 dark:border-zinc-800 dark:text-zinc-500">
        © {new Date().getFullYear()} StatFlow. All rights reserved.
      </footer>
    </div>
  );
}
