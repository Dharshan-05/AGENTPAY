import Link from "next/link";

export default function MaintenancePage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-100">
          <svg className="h-6 w-6 text-yellow-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
        <h1 className="mt-4 text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Under Maintenance
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          We're currently performing scheduled maintenance. Please check back soon.
        </p>
        <div className="mt-6 flex items-center justify-center gap-4">
          <Link href="/" className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            Return to Homepage
          </Link>
          <Link href="/contact" className="rounded-md border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Get Notified When Back
          </Link>
        </div>
      </div>
    </div>
  );
}