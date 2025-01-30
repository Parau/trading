
interface LogoSiteProps {
  size?: number;
}

export function LogoSite({ size = 28 }: LogoSiteProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M3 3v18h18" />
      <path d="M18 8l-3 6l-4-10l-5 8" />
      <circle cx="16" cy="8" r="2" />
      <circle cx="11" cy="4" r="2" />
      <circle cx="7" cy="12" r="2" />
    </svg>
  );
}