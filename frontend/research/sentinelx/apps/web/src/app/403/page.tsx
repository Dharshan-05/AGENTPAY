import Link from "next/link";

export default function ForbiddenPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4M7.206 8.806a4.487 4.487 0 00-1.765 5.97L6 18a2 2 0 002 2h8a2 2 0 002-2l.794-3.224a4.487 4.487 0 00-1.765-5.97l1.071-4.396A1.942 1.942 0 0014.256 4H9.744a1.942 1.942 0 00-1.538 2.41l1.071 4.396z" />
          </svg>
        </div>
        <h1 className="mt-4 text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Access Forbidden
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          You don't have permission to access this resource.
        </p>
        <div className="mt-6 flex items-center justify-center gap-4">
          <Link href="/" className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            Return to Homepage
          </Link>
          <Link href="/contact" className="rounded-md border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Contact Support
          </Link>
        </div>
      </div>
    </div>
  );
}