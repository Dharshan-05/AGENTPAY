
export default function DataRetentionPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Data Retention Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Purpose and Scope</h2>
          <p>
            This Data Retention Policy establishes guidelines for how long 
            SentinelX AI retains different types of data and when such data 
            should be securely deleted or anonymized.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Retention Principles</h2>
          <p>
            Our data retention practices are guided by the following principles:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Data is retained only as long as necessary for the purposes 
                for which it was collected</li>
            <li>We comply with applicable legal and regulatory retention requirements</li>
            <li>We balance operational needs with privacy considerations</li>
            <li>Regular reviews ensure data is not retained longer than necessary</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Categories and Retention Periods</h2>
          <p>
            We retain different types of data for varying periods:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Account Information:</strong> Retained for the duration 
                of the account plus 30 days after account closure</li>
            <li><strong>Transaction Records:</strong> Retained for 7 years 
                for financial and audit purposes</li>
            <li><strong>Usage Logs:</strong> Retained for 24 months for 
                analytics and troubleshooting</li>
            <li><strong>Security Logs:</strong> Retained for 36 months for 
                security investigations and compliance</li>
            <li><strong>Support Tickets:</strong> Retained for 24 months 
                for quality improvement and reference</li>
            <li><strong>Analytics Data:</strong> Retained for 18 months 
                for trend analysis and product improvement</li>
            <li><strong>Backup Data:</strong> Retained according to our 
                backup retention schedule (daily: 7 days, weekly: 4 weeks, 
                monthly: 12 months)</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Special Categories of Data</h2>
          <h3 className="text-xl font-semibold mb-2 mt-6>Sensitive Personal Data</h3>
          <p>
            Sensitive personal data (such as health information, biometric data, 
            or data revealing racial or ethnic origin) is retained only as long 
            as strictly necessary and is subject to additional protection measures.
          </p>
          
          <h3 className="text-xl font-semibold mb-2 mt-6>Children's Data</h3>
          <p>
            We do not knowingly collect personal information from children under 
            13. If we become aware of such data, we will delete it immediately.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Deletion and Anonymization</h2>
          <p>
            When data reaches the end of its retention period, we take one of 
            the following actions:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Secure deletion: Data is permanently erased using methods 
                that prevent recovery</li>
            <li>Anonymization: Personal identifiers are removed, leaving 
                only anonymized data for statistical purposes</li>
            <li>Aggregation: Data is combined with other data to prevent 
                identification of individuals</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Legal Holds</h2>
          <p>
            In the event of litigation, regulatory investigation, or other 
            legal proceedings, we may be required to retain certain data 
            beyond the normal retention period. Such data will be clearly 
            marked and excluded from routine deletion processes.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Automated Processes</h2>
          <p>
            We employ automated systems to help ensure compliance with 
            this policy, including:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Scheduled data retention reviews</li>
            <li>Automated deletion workflows</li>
            <li>Monitoring and alerting for policy compliance</li>
            <li>Regular audits of data retention practices</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Data Retention Policy, please 
            contact us at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> privacy@sentinelx.ai<br />
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