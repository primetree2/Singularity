import { ReactNode } from "react";

type Props = {
  children: ReactNode;
  onClick: () => void;
  variant: "primary" | "secondary";
  disabled?: boolean;
  className?: string;
};

export default function Button({ children, onClick, variant, disabled, className }: Props) {
  const base = "px-4 py-2 rounded transition font-medium";
  const styles =
    variant === "primary"
      ? "bg-blue-600 hover:bg-blue-700 text-white"
      : "bg-gray-200 hover:bg-gray-300 text-gray-800";
  const disabledStyle = disabled ? "opacity-50 cursor-not-allowed hover:none" : "";

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${styles} ${disabledStyle} ${className || ""}`}
    >
      {children}
    </button>
  );
}
