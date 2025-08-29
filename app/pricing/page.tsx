"use client";

import React from "react";
import Link from "next/link";
import DashboardLayout from "../dashboard/DashboardLayout";

const PricingPage = () => {
  return (
    <DashboardLayout>
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="container mx-auto py-8">
          <h1 className="text-4xl font-bold text-center mb-8">Pricing Plans</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free Tier */}
            <div className="bg-white shadow-md rounded-lg p-6 text-center">
              <h2 className="text-2xl font-semibold mb-4">Free Tier</h2>
              <p className="text-gray-600 mb-4">$0 / month</p>
              <ul className="text-left space-y-2 mb-6">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> Upload up to 5
                  PDFs
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> 50 credits
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> Basic PDF
                  processing
                </li>
              </ul>
              <button
                className="btn bg-gray-300 text-gray-700 cursor-not-allowed"
                disabled
              >
                Current Plan
              </button>
            </div>
            {/* Pro Tier */}
            <div className="bg-white shadow-md rounded-lg p-6 text-center">
              <h2 className="text-2xl font-semibold mb-4">Pro Tier</h2>
              <p className="text-gray-600 mb-4">Contact for pricing</p>
              <ul className="text-left space-y-2 mb-6">
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> Unlimited PDF
                  uploads
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> 500 credits
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> Advanced PDF
                  processing
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-2">✔</span> Priority
                  support
                </li>
              </ul>
              <Link
                href="/contact"
                className="btn bg-blue-600 text-white shadow-sm hover:bg-blue-700"
              >
                Contact Us
              </Link>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default PricingPage;
