"use client";

import React, { useState } from "react";
import Introduction from "./components/Introduction";
import GettingStarted from "./components/GettingStarted";
import UsingAPI from "./components/UsingAPI";
import styles from "@/styles/Docs.module.css";
import Link from "next/link"; 
// For the navigation bar

const DocsPage = () => {
  const [activeTab, setActiveTab] = useState("introduction");

  const handleTabClick = (tab: string) => {
    setActiveTab(tab);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation Bar */}
      <header className="bg-indigo-600 p-4">
        <nav className="container mx-auto flex justify-between items-center">
          <Link href="/" className="text-white text-lg font-bold">
            Docs
          </Link>
          <ul className="flex space-x-4 text-white">
            <li><Link href="/">Home</Link></li>
            <li><Link href="/about">About</Link></li>
          </ul>
        </nav>
      </header>

      {/* Content Area */}
      <div className="flex flex-col lg:flex-row">
        {/* Sidebar */}
        <nav className={`${styles.sidebar}`}>
          <ul className="space-y-4">
            <li
              className={`cursor-pointer p-2 rounded-lg ${activeTab === "introduction" ? styles.active : ""}`}
              onClick={() => handleTabClick("introduction")}
            >
              Introduction
            </li>
            <li
              className={`cursor-pointer p-2 rounded-lg ${activeTab === "getting-started" ? styles.active : ""}`}
              onClick={() => handleTabClick("getting-started")}
            >
              Getting Started
            </li>
            <li
              className={`cursor-pointer p-2 rounded-lg ${activeTab === "using-api" ? styles.active : ""}`}
              onClick={() => handleTabClick("using-api")}
            >
              Using the API
            </li>
          </ul>
        </nav>

        {/* Main Content */}
        <main className={`${styles.mainContent}`}>
          {activeTab === "introduction" && <Introduction />}
          {activeTab === "getting-started" && <GettingStarted />}
          {activeTab === "using-api" && <UsingAPI />}
        </main>
      </div>
    </div>
  );
};

export default DocsPage;
