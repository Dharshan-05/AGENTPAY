import Link from "next/link";

export default function ContactPage() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Contact Us
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          We're here to help! Whether you have questions, need support, or want 
          to learn more about SentinelX AI, please don't hesitate to reach out.
        </p>
        
        <div className="grid md:grid-cols-2 gap-8 mt-8">
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold mb-4">Get in Touch</h2>
            <p className="text-gray-700">
              Have questions about our products, pricing, or need technical support? 
              We're ready to assist you.
            </p>
            
            <div className="space-y-4">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                    <polyline points="22,6 12,13 2,6"></polyline>
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">Email Support</h3>
                  <p className="text-sm text-gray-600">
                    manthanjaiswal902@gmail.com
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 13.72v3"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">Phone Support</h3>
                  <p className="text-sm text-gray-600">
                    +91 8125629601
                  </p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M12 16v-4"></path>
                    <path d="M8 12h8"></path>
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">Hours of Operation</h3>
                  <p className="text-sm text-gray-600">
                    Monday - Friday: 9:00 AM - 6:00 PM IST<br />
                    Saturday: 10:00 AM - 2:00 PM IST<br />
                    Sunday: Closed
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold mb-4">Common Contact Reasons</h2>
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">General Inquiries</h3>
                <p className="text-sm">
                  Questions about our products, features, or company information.
                </p>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Technical Support</h3>
                <p className="text-sm">
                  Help with installation, configuration, or troubleshooting.
                </p>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Billing Questions</h3>
                <p className="text-sm">
                  Questions about invoices, payments, or subscription changes.
                </p>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Sales & Partnerships</h3>
                <p className="text-sm">
                  Information about enterprise plans, reseller programs, or partnerships.
                </p>
              </div>
              
              <div className="bg-red-50 p-4 rounded-lg">
                <h3 className="font-semibold mb-2">Security Concerns</h3>
                <p className="text-sm">
                  Report security vulnerabilities or privacy concerns.
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="mt-12 pt-8 border-t">
          <h2 className="text-2xl font-semibold mb-4 text-center">Ready to Get Started?</h2>
          <p className="text-center text-gray-600 mb-6">
            Join thousands of organizations trusting SentinelX AI to protect their 
            AI investments.
          </p>
          <div className="flex justify-center space-x-4">
            <Link href="/" className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-transform hover:scale-105">
              Return to Homepage
            </Link>
            <Link href="/login" className="bg-white hover:bg-gray-100 text-gray-800 font-bold py-3 px-6 border border-gray-300 rounded-lg transition-transform hover:scale-105">
              Log In to Your Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}