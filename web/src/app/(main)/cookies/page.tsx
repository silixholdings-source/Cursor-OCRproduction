import React from 'react'

export default function CookiesPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Cookie Policy</h1>
          
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-600 mb-6">
              <strong>Last updated:</strong> {new Date().toLocaleDateString()}
            </p>
            
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">What Are Cookies</h2>
              <p className="text-gray-600 mb-4">
                Cookies are small text files that are placed on your computer or mobile device when you 
                visit our website. They help us provide you with a better experience by remembering your 
                preferences and understanding how you use our site.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">How We Use Cookies</h2>
              <p className="text-gray-600 mb-4">
                We use cookies for several purposes:
              </p>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li><strong>Essential Cookies:</strong> Required for the website to function properly</li>
                <li><strong>Analytics Cookies:</strong> Help us understand how visitors interact with our website</li>
                <li><strong>Preference Cookies:</strong> Remember your settings and preferences</li>
                <li><strong>Marketing Cookies:</strong> Used to deliver relevant advertisements</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Types of Cookies We Use</h2>
              
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Strictly Necessary Cookies</h3>
                <p className="text-gray-600 mb-2">
                  These cookies are essential for the website to function and cannot be switched off.
                </p>
                <ul className="list-disc pl-6 text-gray-600 space-y-1">
                  <li>Session management</li>
                  <li>Security features</li>
                  <li>Load balancing</li>
                </ul>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Analytics Cookies</h3>
                <p className="text-gray-600 mb-2">
                  These cookies help us understand how visitors use our website.
                </p>
                <ul className="list-disc pl-6 text-gray-600 space-y-1">
                  <li>Page views and navigation</li>
                  <li>Time spent on site</li>
                  <li>Error tracking</li>
                </ul>
              </div>

              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Functional Cookies</h3>
                <p className="text-gray-600 mb-2">
                  These cookies enable enhanced functionality and personalization.
                </p>
                <ul className="list-disc pl-6 text-gray-600 space-y-1">
                  <li>Language preferences</li>
                  <li>Theme settings</li>
                  <li>User preferences</li>
                </ul>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Managing Cookies</h2>
              <p className="text-gray-600 mb-4">
                You can control and manage cookies in various ways:
              </p>
              <ul className="list-disc pl-6 text-gray-600 space-y-2">
                <li>Browser settings: Most browsers allow you to refuse or delete cookies</li>
                <li>Cookie consent: Use our cookie consent banner to manage preferences</li>
                <li>Opt-out tools: Use industry-standard opt-out mechanisms</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Third-Party Cookies</h2>
              <p className="text-gray-600">
                We may use third-party services that set their own cookies. These include analytics 
                providers, advertising networks, and social media platforms. Please refer to their 
                respective privacy policies for more information.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
              <p className="text-gray-600">
                If you have any questions about our use of cookies, please contact us at:
              </p>
              <p className="text-gray-600 mt-2">
                Email: privacy@aierpsaas.com<br />
                Address: AI ERP SaaS, San Francisco, CA
              </p>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}


