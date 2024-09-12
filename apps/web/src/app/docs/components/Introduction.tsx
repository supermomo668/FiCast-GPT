import React from "react";

const Introduction = () => {
  return (
    <section className="text-foreground">
      <h1 className="text-3xl font-bold mb-4">Introduction</h1>
      
      <p className="mb-4">
        Welcome to <strong>FiCast</strong>, a Python package designed for creating podcasts enhanced with background music. FiCast 
        allows you to create “LoFi Podcasts,” where AI-generated scripts are overlaid with music aligned to the theme of 
        your podcast.
      </p>
      
      <h2 className="text-2xl font-semibold mb-2">What is FiCast?</h2>
      <p className="mb-4">
        FiCast is a powerful tool for generating automated podcast content. It supports multi-agent conversations where each 
        agent is powered by state-of-the-art language models like GPT-3.5. With FiCast, you can create engaging podcasts 
        that blend thoughtful conversation with ambient music for a seamless experience.
      </p>
      
      <h2 className="text-2xl font-semibold mb-2">Key Features</h2>
      <ul className="list-disc list-inside mb-4">
        <li>AI-generated scripts tailored to your podcast's theme</li>
        <li>Automated multi-agent conversations with customizable roles and personalities</li>
        <li>Background music integration to enhance the listening experience</li>
        <li>Support for popular AI models like GPT-3.5 for conversation generation</li>
      </ul>
      
      <h2 className="text-2xl font-semibold mb-2">How It Works</h2>
      <p className="mb-4">
        FiCast works by generating podcast scripts using AI and then allowing you to overlay these conversations with 
        music tracks that align with your content. Whether you're producing a podcast about technology, health, or any 
        other subject, FiCast simplifies the production process with a few API calls.
      </p>
      
      <p className="mb-4">
        You can define the number of participants, their roles, and even provide descriptions for each participant. 
        FiCast takes care of the rest by producing a well-structured script and automatically adding background music.
      </p>
      
      <p className="mb-4">
        Get started by visiting the <a href="/docs" className="text-indigo-600">documentation</a> to learn more about the API 
        and how you can start creating your own podcasts today.
      </p>
    </section>
  );
};

export default Introduction;
