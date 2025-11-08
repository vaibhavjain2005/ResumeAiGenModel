import React from "react";
import NavBar from "../components/NavBar";
import { Outlet } from "react-router-dom";

function MainLayout() {
  return (
    <>
      <NavBar />
      <Outlet /> {/* This renders the page content (like App or DataForm) */}
    </>
  );
}

export default MainLayout;
