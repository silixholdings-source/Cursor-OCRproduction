import React from 'react'

export default function PartnersPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">Partners</h1>
          
          <div className="prose prose-lg max-w-none">
            <p className="text-gray-600 mb-8">
              Join our partner ecosystem and help businesses transform their invoice processing with AI-powered automation.
            </p>
            
            <section className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Partnership Opportunities</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Technology Partners</h3>
                  <p className="text-gray-600 mb-4">
                    Integrate AI ERP SaaS with your existing software solutions and create seamless workflows.
                  </p>
                  <ul className="list-disc pl-5 text-gray-600 space-y-1">
                    <li>API integrations</li>
                    <li>SDK access</li>
                    <li>Technical support</li>
                  </ul>
                </div>

                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Reseller Partners</h3>
                  <p className="text-gray-600 mb-4">
                    Resell our solutions to your clients and earn competitive commissions.
                  </p>
                  <ul className="list-disc pl-5 text-gray-600 space-y-1">
                    <li>Competitive margins</li>
                    <li>Marketing support</li>
                    <li>Sales training</li>
                  </ul>
                </div>

                <div className="border border-gray-200 rounded-lg p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Consulting Partners</h3>
                  <p className="text-gray-600 mb-4">
                    Help clients implement and optimize their invoice automation processes.
                  </p>
                  <ul className="list-disc pl-5 text-gray-600 space-y-1">
                    <li>Implementation services</li>
                    <li>Training programs</li>
                    <li>Ongoing support</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-12">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Partner Benefits</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Revenue Opportunities</h3>
                  <ul className="list-disc pl-5 text-gray-600 space-y-2">
                    <li>Competitive commission structure</li>
                    <li>Volume-based incentives</li>
                    <li>Recurring revenue opportunities</li>
                    <li>Performance bonuses</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">Support & Resources</h3>
                  <ul className="list-disc pl-5 text-gray-600 space-y-2">
                    <li>Dedicated partner portal</li>
                    <li>Marketing materials and co-op funds</li>
                    <li>Technical training and certification</li>
                    <li>24/7 partner support</li>
                  </ul>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Get Started</h2>
              <p className="text-gray-600 mb-6">
                Ready to become a partner? Contact our partner team to discuss opportunities and get started.
              </p>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-blue-900 mb-3">Contact Our Partner Team</h3>
                <p className="text-blue-800 mb-4">
                  Email: partners@aierpsaas.com<br />
                  Phone: +1 (555) 123-4567
                </p>
                <p className="text-blue-700 text-sm">
                  We&apos;ll respond within 24 hours to discuss partnership opportunities and next steps.
                </p>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}


