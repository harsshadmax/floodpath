// Small stroke icons (no icon library). All are decorative: the buttons that use them carry text labels.
import type { ReactNode } from "react";

function Svg({ children, size = 22 }: { children: ReactNode; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={1.8}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export const DropIcon = () => (
  <Svg size={22}>
    <path d="M12 3.5c3.2 3.9 5.5 6.8 5.5 9.7a5.5 5.5 0 0 1-11 0C6.5 10.300 8.800 7.400 12 3.500Z" />
  </Svg>
);
export const DashboardIcon = () => (
  <Svg>
    <path d="M4 20V11M10 20V5M16 20v-6M22 20H2" />
  </Svg>
);
export const RouteIcon = () => (
  <Svg>
    <circle cx="6" cy="19" r="2" />
    <circle cx="18" cy="5" r="2" />
    <path d="M8 19h7.500a3.500 3.500 0 0 0 0-7h-7a3.500 3.500 0 0 1 0-7H16" />
  </Svg>
);
export const InfoIcon = () => (
  <Svg>
    <circle cx="12" cy="12" r="9" />
    <path d="M12 11v5M12 8h.01" />
  </Svg>
);
export const CalendarIcon = () => (
  <Svg size={16}>
    <rect x="3" y="5" width="18" height="16" rx="2" />
    <path d="M3 10h18M8 3v4M16 3v4" />
  </Svg>
);
