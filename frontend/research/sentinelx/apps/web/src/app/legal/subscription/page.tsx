
export default function SubscriptionPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Subscription Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Subscription Policy outlines the terms and conditions governing 
            subscriptions to SentinelX AI's services.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Subscription Plans</h2>
          <p>
            We offer various subscription plans to meet different needs:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Community Plan:</strong> Free tier for individuals and 
                open-source projects with basic features</li>
            <li><strong>Business Plan:</strong> Monthly subscription for growing 
                teams with advanced features and support</li>
            <li><strong>Enterprise Plan:</strong> Custom pricing for organizations 
                with comprehensive features, dedicated support, and SLAs</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Billing and Payment</h2>
          <p>
            Subscriptions are billed on a recurring basis according to the selected 
            billing cycle (monthly or annual). Payment is required in advance 
            for each billing period.
          </p>
          <p>
            Accepted payment methods include major credit cards and other 
            secure payment options. Payment failures may result in service 
            interruption or suspension.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Price Changes</h2>
          <p>
            We reserve the right to modify subscription prices at any time. 
            Price changes will be communicated at least 30 days in advance 
            and will apply to the next billing cycle following the notice period.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Free Trials</h2>
          <p>
            We may offer free trial periods for certain subscription plans. 
            During a free trial:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>You will have access to premium features for a limited time</li>
            <li>No payment is required during the trial period</li>
            <li>You must provide valid payment information to start the trial</li>
            <li>If not cancelled before the trial ends, your subscription will 
                automatically begin and you will be charged accordingly</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Upgrades and Downgrades</h2>
          <p>
            You can change your subscription plan at any time:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Upgrades take effect immediately and may result in a prorated charge</li>
            <li>Downgrades typically take effect at the start of the next billing cycle</li>
            <li>Feature availability changes immediately upon plan change</li>
            <li>Some data or configurations may not be compatible between plans</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Automatic Renewal</h2>
          <p>
            Unless cancelled, subscriptions automatically renew at the end of 
            each billing period using the payment method on file.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Inactive Accounts</h2>
          <p>
            Accounts that remain inactive for extended periods may be subject to 
            review and potential deactivation in accordance with our policies.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Subscription Policy, please 
            contact us at:
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