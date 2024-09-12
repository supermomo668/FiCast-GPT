"use client";

import { cn } from "@/lib/utils";
import { useState } from "react";
import { LANDING_CHARACTERS, CUSTOM } from "./CHARACTERS";
import { Participant } from "@/app/models/particpants";

interface CharacterSelectorProps {
  onChange: (selected: Set<string>) => void;
}

interface LandingProps {
  onStart: (data: { topic: string; participants: Participant[] }) => void;
}

const MAX_CHARACTERS = 10;

export function CharacterSelector({ onChange }: CharacterSelectorProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [customName, setCustomName] = useState<string>("Custom");
  const [customDescription, setCustomDescription] = useState<string>("");

  function buttonHandler(name: string) {
    return () => {
      const newSelected = new Set(selected);

      if (selected.has(name)) {
        newSelected.delete(name);
      } else if (newSelected.size < MAX_CHARACTERS) {
        newSelected.add(name);
      }

      setSelected(newSelected);
      onChange(newSelected); // Pass selected characters to parent
    };
  }

  const handleCustomChange = () => {
    const newSelected = new Set(selected);
    if (selected.has("Custom")) {
      newSelected.delete("Custom");
    } else {
      newSelected.add("Custom");
    }
    setSelected(newSelected);
    onChange(newSelected);
  };

  return (
    <div className="text-center">
      <h2 className="text-xl font-bold mt-8 mb-4">Hosts</h2>
      <div className="grid grid-cols-3 gap-8 mb-8">
        {LANDING_CHARACTERS.filter((ch) => ch.role === "host").map((ch) => (
          <button
            onClick={buttonHandler(ch.name)}
            key={ch.name}
            className={cn(
              "border-2 border-solid p-3 rounded-2xl flex flex-col items-center justify-center",
              selected.has(ch.name)
                ? "border-white bg-gradient-to-r from-purple-500 to-purple-900"
                : "border-transparent"
            )}
          >
            <div className="flex items-center justify-center w-40 h-40">
              <img
                src={ch.image}
                alt={ch.name}
                className="object-contain rounded-lg"
                style={{ maxWidth: "100%", maxHeight: "100%" }} // Set flexible max size
              />
            </div>
            <br />
            <span className="text-xs">{ch.name}</span>
          </button>
        ))}
      </div>

      <h2 className="text-xl font-bold mt-8 mb-4">Guests</h2>
      <div className="grid grid-cols-3 gap-8">
        {LANDING_CHARACTERS.filter((ch) => ch.role === "guest").map((ch) => (
          <button
            onClick={buttonHandler(ch.name)}
            key={ch.name}
            className={cn(
              "border-2 border-solid p-3 rounded-2xl flex flex-col items-center justify-center",
              selected.has(ch.name)
                ? "border-white bg-gradient-to-r from-purple-500 to-purple-900"
                : "border-transparent"
            )}
          >
            <div className="flex items-center justify-center w-40 h-40">
              <img
                src={ch.image}
                alt={ch.name}
                className="object-contain rounded-lg"
                style={{ maxWidth: "100%", maxHeight: "100%" }} // Set flexible max size
              />
            </div>
            <br />
            <span className="text-xs">{ch.name}</span>
          </button>
        ))}
      </div>

      <h2 className="text-xl font-bold mt-8 mb-4">Custom Participant</h2>
      <div className="mb-8 flex flex-col items-center">
        <button
          onClick={handleCustomChange}
          className={cn(
            "border-2 border-solid p-3 rounded-2xl flex flex-col items-center justify-center",
            selected.has("Custom")
              ? "border-white bg-gradient-to-r from-purple-500 to-purple-900"
              : "border-transparent"
          )}
        >
          <div className="flex items-center justify-center w-40 h-40">
            <img
              src={CUSTOM.image}
              alt={CUSTOM.name}
              className="object-contain rounded-lg"
              style={{ maxWidth: "100%", maxHeight: "100%" }} // Set flexible max size
            />
          </div>
          <br />
          <span className="text-xs">Custom</span>
        </button>

        {selected.has("Custom") && (
          <>
            <input
              type="text"
              placeholder="Enter custom name"
              value={customName}
              onChange={(e) => setCustomName(e.target.value)}
              className="mt-4 py-2 px-4 text-black border-b border-gray-500 focus:outline-none focus:border-b-2"
            />
            <input
              type="text"
              placeholder="Enter custom description"
              value={customDescription}
              onChange={(e) => setCustomDescription(e.target.value)}
              className="mt-4 py-2 px-4 text-black border-b border-gray-500 focus:outline-none focus:border-b-2"
            />
          </>
        )}
      </div>
    </div>
  );
}

export function Landing({ onStart }: LandingProps) {
  const [topic, setTopic] = useState<string>("An interesting topic");
  const [speakers, setSpeakers] = useState<Set<string>>(new Set());

  const handleStart = () => {
    const participants: Participant[] = Array.from(speakers).map((name) => {
      if (name === "Custom") {
        return {
          name: "Custom", // Can be replaced with customName
          description: "Custom character description", // Can be replaced with customDescription
          model: null, // Handled by backend
          role: "guest",
        };
      }

      const character = LANDING_CHARACTERS.find((ch) => ch.name === name);
      return {
        name: character?.name || "Unknown",
        description: character?.description || "No description available",
        model: character?.model || null,
        role: character?.role || "guest",
      };
    });

    console.log("Participants for the podcast:", participants);
    onStart({ topic, participants });
  };

  return (
    <div className="max-w-screen-md text-center">
      <header className="text-center">
        <h1 className="text-6xl font-extrabold">Fantasy Podcast</h1>
        <h2 className="text-xl mt-8">Pick your participants</h2>
      </header>

      <CharacterSelector onChange={setSpeakers} />

      <section className="text-center mb-8 mt-8">
        <h2 className="text-xl">Choose your topic</h2>
        <input
          className="text-lg py-2 px-4 text-white bg-transparent border-b-white border-b focus:border-b-2 focus:outline-none"
          value={topic}
          onChange={(evt) => setTopic(evt.target.value)}
        />
      </section>

      <button
        className="bg-transparent hover:bg-purple-500 text-purple-200 font-semibold hover:text-white py-2 px-4 border border-purple-200 hover:border-transparent rounded"
        onClick={handleStart}
      >
        Start Podcast
      </button>
    </div>
  );
}
