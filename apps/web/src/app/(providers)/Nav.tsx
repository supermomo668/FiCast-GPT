"use client";

import React, { useState, useRef } from "react";
import {
  Avatar,
  Navbar,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
} from "@nextui-org/react";
import NextLink from "next/link";
import { useAuth } from "@/hooks/useAuth"; // Firebase auth hook
import styles from "@/styles/Nav.module.css";
import { CUSTOM } from "@/app/(components)/CHARACTERS"; // Import CHARACTERS directly

export default function Nav() {
  const { user, signOut } = useAuth(); // Use Firebase auth
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  return (
    <Navbar onMenuOpenChange={setIsMenuOpen} className={`${styles.navbar}`}>
      <NavbarContent className={styles["navbar-content"]}>
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="sm:hidden"
        />
        <NextLink href="/" passHref onClick={handleHomeClick}>
          <span className={styles["brand-name"]}>FiCast</span>
        </NextLink>
        <p className={styles["brand-wordmark"]}>
          Knowledgeable Music in Your Ears
        </p>
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <NextLink href="/plans" passHref>
            <button className={styles["button-primary"]}>
              API Plans
              {/* Subscript for Early Bird Special */}
              <sub style={{ fontSize: "0.6rem", marginLeft: "2px", color: "purple" }}>
                Early Bird
              </sub>
            </button>
          </NextLink>
        </NavbarItem>

        <NavbarItem>
          <NextLink href="/docs" passHref>
            <button className={styles["button-primary"]}>API Docs</button>
          </NextLink>
        </NavbarItem>

        <NavbarItem>
          <div className="container mx-auto p-4">
            {!user && (
              <div className="flex flex-col items-center justify-center">
                <NextLink href="/login" passHref>
                  <button className={styles["button-primary"]}>Sign in</button>
                </NextLink>
              </div>
            )}
            {user && (
              <div className="relative" ref={dropdownRef}>
                <button
                  className="flex items-center space-x-2"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <Avatar
                    src={user.photoURL ?? CUSTOM.image}
                    alt={user.displayName ?? "User Avatar"}
                    className="rounded-full w-10 h-10"
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
