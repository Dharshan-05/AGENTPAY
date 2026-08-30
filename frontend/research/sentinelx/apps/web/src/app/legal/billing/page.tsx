
export default function BillingPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Billing Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Billing Policy outlines how SentinelX AI charges for its services 
            and manages the billing process for our customers.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Billing Cycles</h2>
          <p>
            We offer the following billing cycles:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Monthly:</strong> Billed once per month on the same date 
                as the original subscription date</li>
            <li><strong>Annual:</strong> Billed once per year, typically offering 
                a discount compared to monthly billing</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Payment Methods</h2>
          <p>
            We accept the following payment methods:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Major credit cards (Visa, MasterCard, American Express, Discover)</li>
            <li>Secure online payment processors</li>
            <li>Other methods may be available for enterprise customers</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Billing Date and Time</h2>
          <p>
            Charges are typically processed on the anniversary date of your 
            subscription. The exact time of processing may vary but generally 
            occurs during business hours in the merchant's time zone.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Failed Payments</h2>
          <p>
            If a payment attempt fails:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>We will retry the payment according to our retry schedule</li>
            <li>You will receive notification of the payment failure</li>
            <li>Service may be suspended if payment remains unsuccessful</li>
            <li>You will have an opportunity to update your payment information</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Prorated Charges</h2>
          <p>
            In certain circumstances, we may issue prorated charges:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>When upgrading or downgrading your subscription mid-billing cycle</li>
            <li>When starting or ending service mid-billing cycle</li>
            <li>When adding or removing services or users partway through a period</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Taxes</h2>
          <p>
            Applicable taxes (such as VAT, GST, or sales tax) will be added to 
            your invoice as required by law. Tax rates are determined based on 
            your billing address and the nature of the services provided.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Invoice Delivery</h2>
          <p>
            Invoices are typically delivered electronically via email to the 
            address on file. You can also access and download invoices from 
            your account dashboard.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Payment Due Date</h2>
          <p>
            Payment is due upon receipt of the invoice. Late payments may 
            result in service interruption, late fees, or collection actions.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Currency</h2>
          <p>
            All prices are displayed in and charged in United States Dollars (USD) 
            unless otherwise specified in a custom enterprise agreement.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Billing Support</h2>
          <p>
            If you have any questions about your bill or need assistance with 
            billing matters, please contact us at:
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
