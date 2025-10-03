import React from 'react'

export default function StatusPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">System Status</h1>
          
          <div className="prose prose-lg max-w-none">
            <div className="mb-8">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <span className="text-xl font-semibold text-green-600">All Systems Operational</span>
              </div>
              <p className="text-gray-600">
                All services are running normally. No incidents reported.
              </p>
            </div>
            
            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Service Status</h2>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="font-medium text-gray-900">API Services</span>
                  </div>
                  <span className="text-green-600 font-medium">Operational</span>
                </div>

                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="font-medium text-gray-900">Web Application</span>
                  </div>
                  <span className="text-green-600 font-medium">Operational</span>
                </div>

                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="font-medium text-gray-900">Database</span>
                  </div>
                  <span className="text-green-600 font-medium">Operational</span>
                </div>

                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="font-medium text-gray-900">File Processing</span>
                  </div>
                  <span className="text-green-600 font-medium">Operational</span>
                </div>

                <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                    <span className="font-medium text-gray-900">Email Services</span>
                  </div>
                  <span className="text-green-600 font-medium">Operational</span>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Performance Metrics</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
                  <div className="text-gray-600">Uptime (Last 30 days)</div>
                </div>

                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">45ms</div>
                  <div className="text-gray-600">Average Response Time</div>
                </div>

                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-3xl font-bold text-blue-600 mb-2">0</div>
                  <div className="text-gray-600">Active Incidents</div>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-6">Recent Updates</h2>
              
              <div className="space-y-4">
                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">Scheduled Maintenance</span>
                    <span className="text-sm text-gray-500">December 15, 2024</span>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Routine maintenance completed successfully. All services restored.
                  </p>
                </div>

                <div className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-gray-900">Feature Update</span>
                    <span className="text-sm text-gray-500">December 10, 2024</span>
                  </div>
                  <p className="text-gray-600 text-sm">
                    Enhanced invoice processing accuracy and improved user interface.
                  </p>
                </div>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">Subscribe to Updates</h2>
              <p className="text-gray-600 mb-4">
                Get notified about system status updates and incidents via email.
              </p>
              <div className="flex space-x-2">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  Subscribe
                </button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}


