
export default function CancellationPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Cancellation Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Cancellation Policy outlines how customers can cancel their 
            subscriptions or services with SentinelX AI.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">How to Cancel</h2>
          <p>
            You can cancel your subscription or service at any time by:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Logging into your account and navigating to Account Settings</li>
            <li>Selecting the "Subscription" or "Billing" section</li>
            <li>Choosing the "Cancel Subscription" option</li>
            <li>Following the prompts to confirm your cancellation</li>
          </ul>
          <p>
            Alternatively, you can contact our support team to request cancellation.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Effective Date of Cancellation</h2>
          <p>
            Cancellations are effective immediately upon confirmation, unless 
            otherwise specified. You will continue to have access to your service 
            until the end of the current billing period for which you have already paid.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Billing After Cancellation</h2>
          <p>
            After your cancellation is processed:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>You will not be charged for any future billing periods</li>
            <li>You will receive a confirmation email of your cancellation</li>
            <li>No further payments will be collected unless you reactivate your service</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Access After Cancellation</h2>
          <p>
            After cancellation, you will have:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Access to your account data until the end of the current paid period</li>
            <li>Ability to export your data before your account is deactivated</li>
            <li>Account deactivation following the end of your paid period</li>
            <li>Data retention in accordance with our Data Retention Policy</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Reactivation</h2>
          <p>
            If you wish to reactivate your service after cancellation:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>You can log in to your account and follow the reactivation prompts</li>
            <li>Your account will be restored with your previous settings and data</li>
            <li>Billing will resume at the current rate for your selected plan</li>
            <li>Some promotional pricing may not be available upon reactivation</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Special Circumstances</h2>
          <p>
            In certain situations, different cancellation procedures may apply:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Free trial cancellations can be performed at any time during the trial period</li>
            <li>Enterprise contracts may have specific termination clauses and notice periods</li>
            <li>Promotional or discounted services may have specific cancellation terms</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Cancellation Policy, please contact us at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> support@sentinelx.ai<br />
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