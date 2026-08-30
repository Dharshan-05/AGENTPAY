
export default function SecurityPolicy() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Security Policy
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Our Security Commitment</h2>
          <p>
            At SentinelX AI, security is not just a feature—it's foundational to 
            everything we do. We are committed to protecting our platform, our 
            users' data, and maintaining the trust placed in us.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Information Security Program</h2>
          <p>
            We maintain a comprehensive information security program that includes:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Regular security assessments and penetration testing</li>
            <li>Security awareness training for all employees</li>
            <li>Incident response and recovery procedures</li>
            <li>Third-party security assessments and audits</li>
            <li>Continuous monitoring for security threats and vulnerabilities</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Data Protection</h2>
          <p>
            We employ multiple layers of security to protect your data:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Encryption at rest and in transit using industry-standard algorithms</li>
            <li>Strong access controls and authentication mechanisms</li>
            <li>Regular data backups and disaster recovery procedures</li>
            <li>Data minimization and retention policies</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Network and Infrastructure Security</h2>
          <p>
            Our infrastructure is protected by:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Firewalls and intrusion detection/prevention systems</li>
            <li>Secure network architecture and segmentation</li>
            <li>Regular vulnerability scanning and patch management</li>
            <li>Distributed Denial of Service (DDoS) protection</li>
            <li>Secure configuration management</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Application Security</h2>
          <p>
            We follow secure software development practices, including:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Regular code reviews and security testing</li>
            <li>Static and dynamic application security testing (SAST/DAST)</li>
            <li>Dependency vulnerability scanning</li>
            <li>Security considerations throughout the software development lifecycle</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Authentication and Access Control</h2>
          <p>
            We implement strong authentication and authorization mechanisms:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Multi-factor authentication options</li>
            <li>Role-based access control (RBAC)</li>
            <li>Session management and timeout controls</li>
            <li>Secure password policies and storage</li>
            <li>Regular access privilege reviews</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Monitoring and Logging</h2>
          <p>
            We maintain comprehensive logging and monitoring capabilities:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Centralized logging of security-relevant events</li>
            <li>Real-time alerting for security incidents</li>
            <li>Audit trails for critical system changes</li>
            <li>Regular log analysis and review</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Vulnerability Management</h2>
          <p>
            We have established procedures for identifying, reporting, and addressing 
            security vulnerabilities:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Regular vulnerability assessments and penetration testing</li>
            <li>Coordinated vulnerability disclosure process</li>
            <li>Timely patching and remediation of identified vulnerabilities</li>
            <li>Third-party security researcher collaboration</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Incident Response</h2>
          <p>
            In the event of a security incident, we follow established procedures 
            to:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Quickly identify and contain the incident</li>
            <li>Eradicate the threat and recover affected systems</li>
            <li>Conduct thorough forensic analysis</li>
            <li>Notify affected parties in accordance with legal requirements</li>
            <li>Implement corrective actions to prevent recurrence</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Compliance and Regulations</h2>
          <p>
            We strive to comply with applicable data protection and security 
            regulations, including:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>General Data Protection Regulation (GDPR) principles</li>
            <li>California Consumer Privacy Act (CCPA) considerations</li>
            <li>Industry-specific security standards and best practices</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            If you have any security concerns or wish to report a potential 
            vulnerability, please contact us at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> security@sentinelx.ai<br />
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