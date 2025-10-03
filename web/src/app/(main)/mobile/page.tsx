import React from 'react';

export default function MobilePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="container mx-auto px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Mobile Apps
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Access AI ERP SaaS on the go with our powerful mobile applications for iOS and Android.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            {/* iOS App */}
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="w-16 h-16 bg-black rounded-2xl flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">iOS App</h3>
              <p className="text-gray-600 mb-6">
                Download our iOS app from the App Store to manage your invoices and business operations on your iPhone or iPad.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>iPhone and iPad compatible</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>iOS 14.0 or later</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>Offline mode support</span>
                </div>
              </div>
              <div className="mt-6">
                <a 
                  href="https://apps.apple.com/app/ai-erp-saas" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-black text-white px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
                >
                  Download for iOS
                </a>
              </div>
            </div>

            {/* Android App */}
            <div className="bg-white rounded-lg shadow-md p-8 text-center">
              <div className="w-16 h-16 bg-green-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                <svg className="w-8 h-8 text-white" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4486.9993.9993.0001.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4486.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.416.416 0 00-.5676.1521l-2.0223 3.503C15.5902 8.2439 13.8533 7.8508 12 7.8508s-3.5902.3931-5.1367 1.5559L4.841 5.9037a.416.416 0 00-.5676-.1521.416.416 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6889-7.5743-6.1185-9.4396"/>
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Android App</h3>
              <p className="text-gray-600 mb-6">
                Get our Android app from Google Play to access your business tools and invoice management on your Android device.
              </p>
              <div className="space-y-3">
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>All Android devices</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>Android 8.0 or later</span>
                </div>
                <div className="flex items-center justify-center text-sm text-gray-500">
                  <span className="mr-2">✓</span>
                  <span>Push notifications</span>
                </div>
              </div>
              <div className="mt-6">
                <a 
                  href="https://play.google.com/store/apps/details?id=com.aierpsaas.app" 
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors"
                >
                  Download for Android
                </a>
              </div>
            </div>
          </div>

          {/* Features Section */}
          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <h2 className="text-2xl font-bold text-center mb-8">Mobile App Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Invoice Scanning</h3>
                <p className="text-gray-600 text-sm">Capture and process invoices on the go with AI-powered OCR technology.</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Real-time Analytics</h3>
                <p className="text-gray-600 text-sm">Monitor your business performance with live dashboards and reports.</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Mobile Dashboard</h3>
                <p className="text-gray-600 text-sm">Access all your business tools and data from a single mobile interface.</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 19h6v2H4a2 2 0 01-2-2V5a2 2 0 012-2h6v2H4v14z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Quick Approvals</h3>
                <p className="text-gray-600 text-sm">Approve invoices and expenses quickly with touch-friendly interfaces.</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5v-5zM4 19h6v2H4a2 2 0 01-2-2V5a2 2 0 012-2h6v2H4v14z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Offline Mode</h3>
                <p className="text-gray-600 text-sm">Work without internet connection and sync when you&apos;re back online.</p>
              </div>

              <div className="text-center">
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2">Push Notifications</h3>
                <p className="text-gray-600 text-sm">Stay updated with real-time notifications for important business events.</p>
              </div>
            </div>
          </div>

          {/* Coming Soon Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-md p-8 text-white text-center">
            <h2 className="text-2xl font-bold mb-4">Coming Soon</h2>
            <p className="text-blue-100 mb-6">
              Our mobile apps are currently in development. Sign up to be notified when they&apos;re ready for download.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/auth/register" 
                className="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg"
              >
                Get Early Access
              </a>
              <a 
                href="/contact" 
                className="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 hover:scale-105 shadow-lg"
              >
                Contact Us
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


