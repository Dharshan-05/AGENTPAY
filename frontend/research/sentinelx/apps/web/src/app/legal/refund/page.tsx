
export default function RefundPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Refund Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Refund Policy outlines the circumstances under which SentinelX AI 
            will provide refunds for payments made for our services.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Eligibility for Refunds</h2>
          <p>
            Refunds may be considered in the following circumstances:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Service not provided as described in our service agreement</li>
            <li>Technical issues preventing access to our service for an extended period</li>
            <li>Duplicate payments made for the same service</li>
            <li>Errors in billing or invoice generation</li>
            <li>Cancellation within the applicable refund window (if any)</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Non-Refundable Circumstances</h2>
          <p>
            The following circumstances are generally not eligible for refunds:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Change of mind or dissatisfaction with service results</li>
            <li>Services already consumed or used</li>
            <li>Violation of our Terms of Service resulting in account termination</li>
            <li>Payments for services rendered in accordance with our agreement</li>
            <li>Fees for optional add-ons or premium features that were accessed</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Refund Process</h2>
          <p>
            To request a refund, please follow these steps:
          </p>
          <ol className="list-decimal list-inside space-y-2 mt-4">
            <li>Contact our support team at manthanjaiswal902@gmail.com</li>
            <li>Provide your account information and details of the payment in question</li>
            <li>Explain the reason for your refund request</li>
            <li>Allow 5-10 business days for our team to review your request</li>
            <li>If approved, refunds will be issued to the original payment method</li>
          </ol>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Refund Timing</h2>
          <p>
            Approved refunds are typically processed within 5-10 business days. 
            The time it takes for the refund to appear in your account may vary 
            depending on your payment method and financial institution.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Partial Refunds</h2>
          <p>
            In some cases, we may offer partial refunds for services that were 
            partially delivered or for which only certain features were inaccessible.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Subscription Refunds</h2>
          <p>
            For subscription-based services:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Refunds are generally not provided for partially used subscription periods</li>
            <li>Cancellation stops future billing but does not entitle you to a refund 
                for the current billing period</li>
            <li>Exceptions may be made for service outages or failures to deliver 
                promised functionality</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Refund Policy, please contact us at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> billing@sentinelx.ai<br />
            <strong>Phone:</strong> +91 8125629601
          </p>
        </div>
        
        <div className="mt-10 text-center text-sm text-gray-500 border-t pt-6">
          © 2026 SentinelX AI. All rights reserved.
        </div>
      </div>
    </div>
  );
}