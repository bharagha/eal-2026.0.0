import { createBrowserRouter } from "react-router";
import Home from "@/pages/Home.tsx";
import Pipelines from "@/pages/Pipelines.tsx";
import Layout from "@/Layout.tsx";
import Models from "@/pages/Models.tsx";
import Videos from "@/pages/Videos.tsx";
import PerformanceTests from "@/pages/PerformanceTests.tsx";
import DensityTests from "@/pages/DensityTests.tsx";

export default createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Home },
      { path: "pipelines/:id", Component: Pipelines },
      { path: "models", Component: Models },
      { path: "videos", Component: Videos },
      { path: "tests/performance", Component: PerformanceTests },
      { path: "tests/density", Component: DensityTests },
    ],
  },
]);
