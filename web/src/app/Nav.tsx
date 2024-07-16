"use client";
import React, { useState } from "react";
import { useSession, signIn, signOut } from "next-auth/react";
import {
  Avatar,
  Badge,
  Button,
  Link,
  Navbar,
  NavbarBrand,
  NavbarContent,
  NavbarItem,
  NavbarMenu,
  NavbarMenuItem,
  NavbarMenuToggle,
  Spinner,
  Switch,
} from "@nextui-org/react";
import NextLink from "next/link";
import { useTheme } from "next-themes";
import { useSelectedLayoutSegment } from "next/navigation";

export default function Nav() {
  const { data: session, status } = useSession();
  const { user } = session || {};
  const isSubscribed = user?.subscriptionStatus === "active" || false;
  const segment = useSelectedLayoutSegment();
  const { theme, setTheme } = useTheme();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <Navbar onMenuOpenChange={setIsMenuOpen} className="mt-2">
      <NavbarContent>
        <NavbarMenuToggle
          aria-label={isMenuOpen ? "Close menu" : "Open menu"}
          className="sm:hidden"
        />
        <NavbarBrand>
          <p className="font-bold text-inherit hidden sm:flex pl-4">
            FiCast-GPT
          </p>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <div className="container mx-auto p-4">
            {!session && (
              <div className="flex flex-col items-center justify-center">
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => signIn()}
                >
                  Sign in
                </button>
              </div>
            )}
            {session && (
              <div className="flex flex-col items-center justify-center">
                <button
                  className="btn btn-outline btn-primary btn-sm"
                  onClick={() => signOut()}
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
}
