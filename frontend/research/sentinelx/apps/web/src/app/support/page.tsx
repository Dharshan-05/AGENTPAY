
export default function SupportPage() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Support Center
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8">Our Commitment to Support</h2>
          <p>
            At SentinelX AI, we're dedicated to providing exceptional support to 
            ensure your success with our AI governance firewall platform.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Support Channels</h2>
          <p>
            We offer multiple ways to get the help you need:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Email Support:</strong> manthanjaiswal902@gmail.com</li>
            <li><strong>Phone Support:</strong> +91 8125629601 (Business hours)</li>
            <li><strong>Documentation:</strong> Comprehensive guides and tutorials</li>
            <li><strong>Community Forum:</strong> Ask questions and share knowledge</li>
            <li><strong>In-App Help:</strong> Contextual help within our platform</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Support Tiers</h2>
          <p>
            Different subscription plans receive different levels of support:
          </p>
          <div className="space-y-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Community Support</h3>
              <p className="text-sm">
                Access to community forums, documentation, and self-help resources.
                Ideal for individuals and small teams getting started.
              </p>
            </div>
            
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Standard Support</h3>
              <p className="text-sm">
                Email support with 24-hour response time, access to knowledge base, 
                and basic troubleshooting assistance.
              </p>
            </div>
            
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Priority Support</h3>
              <p className="text-sm">
                Faster response times, extended hours access, and priority routing 
                for critical issues.
              </p>
            </div>
            
            <div className="bg-red-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Enterprise Support</h3>
              <p className="text-sm">
                24/7 phone, email, and chat support, dedicated technical account 
                manager, and customized support plans.
              </p>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Support Hours</h2>
          <p>
            Our support team is available during the following hours:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li><strong>Standard Support:</strong> Monday-Friday, 9:00 AM - 6:00 PM IST</li>
            <li><strong>Extended Support:</strong> Saturday, 10:00 AM - 2:00 PM IST</li>
            <li><strong>Emergency Support:</strong> 24/7 for critical severity issues (Enterprise only)</li>
            <li><strong>Holiday Schedule:</strong> Limited support on major holidays</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">How to Get the Best Support</h2>
          <p>
            To help us help you more effectively, please provide:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Your account ID or organization name</li>
            <li>A clear description of the issue or question</li>
            <li>Steps to reproduce the problem (if applicable)</li>
            <li>Any error messages or screenshots</li>
            <li>Your preferred contact method and timing</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Self-Service Resources</h2>
          <p>
            Before contacting support, you may find answers in our self-service resources:
          </p>
          <ul className="list-disc list-inside space-y-2 mt-4">
            <li>Knowledge Base: Searchable articles and guides</li>
            <li>Video Tutorials: Step-by-step walkthroughs of common tasks</li>
            <li>API Documentation: Complete reference for developers</li>
            <li>Release Notes: Information about new features and fixes</li>
            <li>Status Page: Real-time information about system availability</li>
          </ul>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8">Contact Us</h2>
          <p>
            Ready to get help? Reach out to our support team at:
          </p>
          <p className="bg-gray-50 p-4 rounded-lg">
            <strong>Email:</strong> support@sentinelx.ai<br />
            <strong>Phone:</strong> +91 8125629601<br />
            <strong>Hours:</strong> Monday-Friday: 9:00 AM - 6:00 PM IST
          </p>
        </div>
        
        <div className="mt-10 text-center text-sm text-gray-500 border-t pt-6">
          © 2026 SentinelX AI. All rights reserved.
        </div>
      </div>
    </div>
  );
}