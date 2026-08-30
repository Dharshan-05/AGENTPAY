
export default function ServiceLevelOverview() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Service Level Overview
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Overview</h2>
          <p>
            This Service Level Overview describes the levels of service, support, 
            and performance that customers can expect from SentinelX AI's services.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Service Availability</h2>
          <p>
            We strive to provide high availability for our services:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Community Plan:</strong> Best effort availability</li>
            <li><strong>Business Plan:</strong> 99.9% monthly uptime</li>
            <li><strong>Enterprise Plan:</strong> 99.95% monthly uptime with financially backed SLA</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Support Levels</h2>
          <p>
            Different subscription tiers receive different levels of support:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Community Plan:</strong> Community forums and documentation</li>
            <li><strong>Business Plan:</strong> Email support with 24-hour response time</li>
            <li><strong>Enterprise Plan:</strong> 
                <ul className="list-disc pl-5 mt-2">
                    <li>24/7 phone, email, and chat support</li>
                    <li>Dedicated technical account manager</li>
                    <li>1-hour response time for critical issues</li>
                    <li>On-site support available (additional fees may apply)</li>
                </ul>
            </li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Response Times</h2>
          <p>
            Our target response times for support inquiries are:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Critical Issues (Service Down):</strong> 1 hour</li>
            <li><strong>High Priority (Major Feature Broken):</strong> 4 hours</li>
            <li><strong>Medium Priority (Minor Bug or Question):</strong> 8 hours</li>
            <li><strong>Low Priority (General Inquiry):</strong> 24 hours</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Performance Standards</h2>
          <p>
            We aim to maintain the following performance standards:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>API Response Time:</strong> &lt; 200ms for 95% of requests</li>
            <li><strong>Dashboard Load Time:</strong> &lt; 3 seconds for standard views</li>
            <li><strong>AI Processing Time:</strong> &lt; 1 second for standard queries</li>
            <li><strong>Report Generation:</strong> &lt; 5 seconds for standard reports</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Maintenance Windows</h2>
          <p>
            Scheduled maintenance typically occurs:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>During off-peak hours (2:00 AM - 5:00 AM UTC)</li>
            <li>No more than 4 hours per month for standard maintenance</li>
            <li>Advanced notice provided for maintenance affecting service availability</li>
            <li>Emergency maintenance performed as needed with minimal notice</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Disaster Recovery</h2>
          <p>
            We have comprehensive disaster recovery measures in place:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Regular backups of all critical data</li>
            <li>Geographically distributed data centers</li>
            <li>Automated failover systems</li>
            <li>Regular disaster recovery testing</li>
            <li>Recovery Time Objective (RTO): &lt; 4 hours</li>
            <li>Recovery Point Objective (RPO): &lt; 1 hour</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any questions about our Service Level Overview, please 
            contact us at:
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