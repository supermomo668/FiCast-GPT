"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function Plans() {
  const [selectedPlan, setSelectedPlan] = useState<string>("freemium");
  const router = useRouter();

  const handleProceed = () => {
    router.push("/payment");
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-slate-900 to-purple-900/30">
      <h1 className="text-5xl font-bold mb-8">Choose Your Plan</h1>
      <div className="flex space-x-10">
        {/* FREEMIUM Plan */}
        <div
          className={`border-4 rounded-lg p-8 cursor-pointer text-center transition-all ${
            selectedPlan === "freemium" ? "border-purple-700" : "border-gray-500"
          }`}
          style={{ width: "300px", borderWidth: "4px" }} // Consistent width
          onClick={() => setSelectedPlan("freemium")}
        >
          <h2 className="text-3xl font-bold">FREEMIUM</h2>
          <p className="text-xl mt-2">Free</p> {/* Subtitle for price */}
          <ul className="mt-4 text-center">
            <li>✔ Limited to 2 participants</li>
            <li>✔ Basic podcast generation</li>
            <li>✔ Standard AI model</li>
          </ul>
        </div>
        
        {/* CREATIVE Plan with Rainbowy Border */}
        <div
          className={`rounded-lg p-8 cursor-pointer text-center transition-all ${
            selectedPlan === "premium" ? "animate-border" : ""
          }`}
          style={{
            width: "300px",
            borderWidth: "4px",
            background: selectedPlan === "premium"
              ? "linear-gradient(darkslateblue, indigo) padding-box, linear-gradient(90deg, red, orange, yellow, green, blue, indigo, violet) border-box"
              : "none",
            border: selectedPlan === "premium" ? "4px solid transparent" : "border-gray-500",
          }}
          onClick={() => setSelectedPlan("premium")}
        >
          <h2 className="text-3xl font-bold">CREATIVE</h2>
          <p className="text-xl mt-2">$5/mo</p> {/* Subtitle for price */}
          <ul className="mt-4 text-center">
            <li>✔ Unlimited participants</li>
            <li>✔ Advanced AI model</li>
            <li>✔ Customizable podcast options</li>
            <li>✔ ... and more!</li>
          </ul>
        </div>
      </div>
      
      <button
        className={`mt-8 px-6 py-3 rounded bg-purple-500 text-white ${
          selectedPlan ? "" : "opacity-50 cursor-not-allowed"
        }`}
        onClick={handleProceed}
        disabled={!selectedPlan}
      >
        Proceed
      </button>
    </div>
  );
}
