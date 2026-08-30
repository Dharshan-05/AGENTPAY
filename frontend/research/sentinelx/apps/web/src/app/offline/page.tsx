"use client";

export default function OfflinePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-blue-100">
          <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h1 className="mt-4 text-3xl font-extrabold text-gray-900 sm:text-4xl">
          You're Offline
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          It looks like you've lost your internet connection. Please check your network and try again.
        </p>
        <div className="mt-6 flex items-center justify-center gap-4">
          <button
            onClick={() => window.location.reload()}
            className="rounded-md bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Try Again
          </button>
          <a href="/" className="rounded-md border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Go to Homepage
          </a>
        </div>
      </div>
    </div>
  );
}