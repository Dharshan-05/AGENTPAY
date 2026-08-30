import Link from "next/link";

export default function UnauthorizedPage() {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-red-100">
          <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.236 3 1.732 3z" />
          </svg>
        </div>
        <h1 className="mt-4 text-3xl font-extrabold text-gray-900 sm:text-4xl">
          Unauthorized
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          You must be logged in to view this page.
        </p>
        <div className="mt-6 flex items-center justify-center gap-4">
          <Link href="/" className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700">
            Return to Homepage
          </Link>
          <Link href="/login" className="rounded-md border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50">
            Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}