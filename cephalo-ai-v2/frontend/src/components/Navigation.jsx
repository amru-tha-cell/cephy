
import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Brain,
  FileText,
  ChartNoAxesCombined,
} from "lucide-react";

const Navigation = () => {
  const links = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Analysis",
      path: "/analysis",
      icon: Brain,
    },
    {
      name: "Reports",
      path: "/reports",
      icon: FileText,
    },
    {
      name: "Analytics",
      path: "/analytics",
      icon: ChartNoAxesCombined,
    },
  ];

  return (
    <nav className="main-navigation">
      <div className="navigation-brand">
        <Brain size={24} />
        <span>Cephalo AI</span>
      </div>

      <div className="navigation-links">
        {links.map((link) => {
          const Icon = link.icon;

          return (
            <NavLink
              key={link.path}
              to={link.path}
              end={link.path === "/"}
              className={({ isActive }) =>
                `navigation-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={18} />
              <span>{link.name}</span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};

export default Navigation;
