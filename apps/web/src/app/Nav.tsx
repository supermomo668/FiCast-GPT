"use client";
import React, { useState, useEffect, useRef } from "react";
import { useSession, signIn, signOut } from "next-auth/react";
import {
  Avatar,
  Button,
  Navbar,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
} from "@nextui-org/react";
import NextLink from "next/link";

export default function Nav() {
  const { data: session, status } = useSession();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleSignOut = () => {
    signOut();
    setIsDropdownOpen(false);
  };

  const handleProfileClick = () => {
    setIsDropdownOpen(false);
  };

  const handleHomeClick = () => {
    setIsDropdownOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownRef]);

  return (
    <Navbar
      onMenuOpenChange={setIsMenuOpen}
      className="mt-2 bg-gray-800 text-white"
    >
      <NavbarContent>
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="sm:hidden"
        />
        <NextLink href="/" passHref onClick={handleHomeClick}>
          FiCast-GPT
        </NextLink>
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <div className="container mx-auto p-4">
            {!session && (
              <div className="flex flex-col items-center justify-center">
                <Button
                  className="btn btn-primary btn-sm"
                  onClick={() => signIn()}
                >
                  Sign in
                </Button>
              </div>
            )}
            {session && (
              <div className="relative" ref={dropdownRef}>
                <button
                  className="flex items-center space-x-2"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <Avatar
                    src={session.user.image}
                    alt={session.user.name}
                    className="rounded-full w-10 h-10" // Tailwind CSS classes for size
                  />
                </button>
                {isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-gray-700 border border-gray-600 rounded shadow-lg">
                    <NextLink href="/profile" passHref>
                      <div
                        className="block px-4 py-2 text-sm text-white hover:bg-gray-600 cursor-pointer"
                        onClick={handleProfileClick}
                      >
                        Profile
                      </div>
                    </NextLink>
                    <div
                      className="block w-full text-left px-4 py-2 text-sm text-white hover:bg-gray-600 cursor-pointer"
                      onClick={handleSignOut}
                    >
                      Sign out
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
}
