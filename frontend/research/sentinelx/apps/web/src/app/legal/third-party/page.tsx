
export default function ThirdPartyNotices() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Third Party Notices
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8>Overview</h2>
          <p>
            This document contains notices for third party software that may be 
            embedded within or distributed alongside SentinelX AI software.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>Attribution Requirements</h2>
          <p>
            Certain third party components used in our software require specific 
            attribution notices. The following notices are provided in accordance 
            with the terms of the accompanying licenses.
          </p>
          
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Mapbox GL JS</h3>
              <p className="text-sm">BSD 3-Clause License</p>
              <div className="border-t pt-3 mt-3 text-xs">
                © 2026 Mapbox. All rights reserved.<br />
                Licensed under the BSD 3-Clause License.
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Elasticsearch</h3>
              <p className="text-sm">Apache License 2.0</p>
              <div className="border-t pt-3 mt-3 text-xs">
                © 2026 Elasticsearch BV. All rights reserved.<br />
                Licensed under the Apache License, Version 2.0.
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Apache Kafka</h3>
              <p className="text-sm">Apache License 2.0</p>
              <div className="border-t pt-3 mt-3 text-xs">
                © 2026 The Apache Software Foundation. All rights reserved.<br />
                Licensed under the Apache License, Version 2.0.
              </div>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>How to Access Complete Notices</h2>
          <p>
            For a complete list of all third party notices and full license texts, 
            please refer to the THIRDPARTY.txt file located in the root directory 
            of our software distribution or contact our legal department.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>Contact Us</h2>
          <p>
            If you have any questions about third party notices, please contact us 
            at:
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