
export default function OpenSourceLicenses() {
  return (
    <div className="container mx-auto px-4 py-8 md:py-16">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 text-center">
          Open Source Licenses
        </h1>
        <p className="text-gray-600 mb-4 text-center">
          Last updated: August 6, 2026
        </p>
        
        <div className="prose lg:prose-xl max-w-none">
          <h2 className="text-2xl font-semibold mb-4 mt-8>Overview</h2>
          <p>
            SentinelX AI makes use of various open source components in our 
            products and services. We are committed to complying with the terms 
            of all open source licenses used in our software.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>Used Open Source Components</h2>
          <p>
            Our software includes the following open source components:
          </p>
          
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Next.js</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                A React framework for building fast and scalable web applications.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">React</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                A JavaScript library for building user interfaces.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">TypeScript</h3>
              <p className="text-sm">Apache License 2.0</p>
              <p className="text-xs text-gray-500">
                A typed superset of JavaScript that compiles to plain JavaScript.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Tailwind CSS</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                A utility-first CSS framework for rapidly building custom designs.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Framer Motion</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                A production-ready motion library for React.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Zustand</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                A small, fast and scalable bearbones state-management solution.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Headless UI</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                Completely unstyled, fully accessible UI components, designed to 
                integrate beautifully with Tailwind CSS.
              </p>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="font-semibold mb-2">Heroicons</h3>
              <p className="text-sm">MIT License</p>
              <p className="text-xs text-gray-500">
                Beautiful hand-crafted SVG icons, by the makers of Tailwind CSS.
              </p>
            </div>
          </div>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>License Texts</h2>
          <p>
            Complete license texts for all open source components used in our 
            software are available in the THIRDPARTY.txt file in our repository 
            or can be requested by contacting our legal department.
          </p>
          
          <h2 className="text-2xl font-semibold mb-4 mt-8>Contact Us</h2>
          <p>
            If you have any questions about our use of open source software, 
            please contact us at:
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