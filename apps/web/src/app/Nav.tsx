"use client";

import React, { useState, useRef } from "react";
import { useSession, signOut } from "next-auth/react";
import {
  Avatar,
  Navbar,
  NavbarContent,
  NavbarItem,
  NavbarMenuToggle,
} from "@nextui-org/react";
import NextLink from "next/link";
import styles from "./styles/Nav.module.css";

export default function Nav() {
  const { data: session } = useSession();
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
    <Navbar
      onMenuOpenChange={setIsMenuOpen}
      className={`${styles.navbar}`}
    >
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
          <div className="container mx-auto p-4">
            {!session && (
              <div className="flex flex-col items-center justify-center">
                <NextLink href="/login" passHref>
                  <button className={styles["button-primary"]}>
                    Sign in
                  </button>
                </NextLink>
              </div>
            )}
            {session && (
              <div className="relative" ref={dropdownRef}>
                <button
                  className="flex items-center space-x-2"
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                >
                  <Avatar
                    src={session.user.image ?? '/default-avatar.png'}
                    alt={session.user.name ?? 'User Avatar'}
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