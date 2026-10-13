import { Suspense } from "react";
import Dashboard from "@/components/Dashboard";

export default function Home() {
  // useSearchParams (the language lives in the address) needs a Suspense boundary.
  return (
    <Suspense fallback={null}>
      <Dashboard />
    </Suspense>
  );
}
