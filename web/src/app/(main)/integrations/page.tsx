import React from 'react';

export default function IntegrationsPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Integrations
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Connect AI ERP SaaS with your favorite tools and platforms to streamline your workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Popular Integrations */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Accounting Software</h3>
              <ul className="space-y-2">
                <li>• QuickBooks</li>
                <li>• Xero</li>
                <li>• Sage</li>
                <li>• NetSuite</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">ERP Systems</h3>
              <ul className="space-y-2">
                <li>• SAP</li>
                <li>• Oracle</li>
                <li>• Microsoft Dynamics</li>
                <li>• Workday</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-xl font-semibold mb-4">Business Tools</h3>
              <ul className="space-y-2">
                <li>• Slack</li>
                <li>• Microsoft Teams</li>
                <li>• Salesforce</li>
                <li>• HubSpot</li>
              </ul>
            </div>
          </div>

          <div className="text-center mt-12">
            <h2 className="text-2xl font-bold mb-4">Need a Custom Integration?</h2>
            <p className="text-gray-600 mb-6">
              We can build custom integrations for any platform you use.
            </p>
            <a 
              href="/contact" 
              className="inline-block bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Contact Sales
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}


