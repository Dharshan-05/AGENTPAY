
export default function DataProcessingPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Data Processing Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Data Processing Policy ("Policy") describes how SentinelX AI 
            processes personal data on behalf of our customers ("Data Controllers") 
            when providing our AI governance firewall services.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Roles and Responsibilities</h2>
          <p>
            Under this Policy:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Data Controller:</strong> The customer or organization 
                that determines the purposes and means of processing personal data.</li>
            <li><strong>Data Processor:</strong> SentinelX AI, which processes 
                personal data on behalf of the Data Controller.</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Types of Personal Data Processed</h2>
          <p>
            We may process the following categories of personal data:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Contact information (name, email address, phone number)</li>
            <li>Authentication data (hashed passwords, OAuth tokens)</li>
            <li>Usage data (IP addresses, timestamps, feature usage)</li>
            <li>Professional information (job title, department, organization)</li>
            <li>Technical data (system logs, error reports, performance metrics)</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Purposes of Processing</h2>
          <p>
            We process personal data for the following purposes:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Providing and maintaining our AI governance firewall services</li>
            <li>Authenticating users and managing access to our platform</li>
            <li>Detecting and preventing sensitive data leakage to LLMs</li>
            <li>Generating security insights, reports, and analytics</li>
            <li>Improving our services through analysis and feedback</li>
            <li>Ensuring compliance with legal and regulatory requirements</li>
            <li>Providing customer support and technical assistance</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Legal Basis for Processing</h2>
          <p>
            When processing personal data as a data processor, we rely on:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>The data controller's instructions and documented authorization</li>
            <li>Performance of a contract with the data controller</li>
            <li>Compliance with legal obligations</li>
            <li>Legitimate interests pursued by us or by third parties</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Subject Rights</h2>
          <p>
            We assist data controllers in fulfilling their obligations to respect 
            data subject rights, including:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Right to access personal data</li>
            <li>Right to rectification of inaccurate data</li>
            <li>Right to erasure ("right to be forgotten")</li>
            <li>Right to restriction of processing</li>
            <li>Right to data portability</li>
            <li>Right to object to processing</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Transfers</h2>
          <p>
            Personal data may be transferred to:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Subprocessors who assist us in providing our services</li>
            <li>Countries outside the European Economic Area (EEA) with appropriate 
                safeguards in place</li>
            <li>Third parties as required by law or legal process</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Security</h2>
          <p>
            We implement appropriate technical and organizational measures to 
            protect personal data against accidental or unlawful destruction, 
            loss, alteration, unauthorized disclosure, or access.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Retention and Deletion</h2>
          <p>
            We retain personal data only as long as necessary to fulfill the 
            purposes outlined in this Policy or as required by applicable laws.
          </p>
          <p>
            Upon termination of our services, we will delete or return personal 
            data to the data controller in accordance with our agreement.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Subprocessors</h2>
          <p>
            We may engage subprocessors to assist in providing our services. 
            Current subprocessors include:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Cloud infrastructure providers (AWS, Google Cloud, Azure)</li>
            <li>Payment processors</li>
            <li>Email service providers</li>
            <li>Analytics and monitoring services</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Data Processing Policy, please 
            contact us at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> legal@sentinelx.ai<br />
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