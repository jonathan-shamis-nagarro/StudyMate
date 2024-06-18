import React from "react";
import { Link } from "react-router-dom";

const Layout = () => {
  return (
    <>
      <div className="navbar navbar-expand-lg navbar-light bg-light fixed-top">
        <div className="container-fluid">
          <Link to="/" className="navbar-brand">
            <img src="../applogo.png" />
            Study Mate{" "}
          </Link>
        </div>
      </div>
    </>
  );
};

export default Layout;
